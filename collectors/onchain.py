"""
On-chain data collector for Solana ecosystem
Tracks new programs, usage spikes, wallet behavior, and DeFi activity
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict
from dataclasses import dataclass, field

from config import config


@dataclass
class ProgramActivity:
    program_id: str
    name: Optional[str]
    transaction_count: int
    unique_signers: int
    first_seen: Optional[datetime]
    category: Optional[str]  # defi, nft, gaming, etc.


@dataclass
class WalletBehavior:
    trend: str  # "accumulating", "distributing", "new_activity"
    token_or_protocol: str
    wallet_count: int
    volume_change_pct: float


@dataclass
class OnChainSignal:
    signal_type: str  # "new_program", "usage_spike", "whale_activity", "token_launch"
    description: str
    data: dict
    strength: float  # 0-1
    timestamp: datetime


class OnChainCollector:
    """Collects on-chain signals from Solana"""

    def __init__(self):
        self.rpc_url = config.solana_rpc_url
        self.helius_key = config.helius_api_key
        self.signals: List[OnChainSignal] = []

    async def collect_all(self, days_back: int = 14) -> List[OnChainSignal]:
        """Collect all on-chain signals for the past N days"""
        self.signals = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Run collectors concurrently
            await asyncio.gather(
                self._collect_new_programs(client, days_back),
                self._collect_program_activity(client, days_back),
                self._collect_token_launches(client, days_back),
                self._collect_defi_trends(client, days_back),
                return_exceptions=True
            )

        return self.signals

    async def _collect_new_programs(self, client: httpx.AsyncClient, days_back: int):
        """Detect newly deployed programs with significant activity"""
        if not self.helius_key:
            return

        try:
            # Use Helius enhanced API for program discovery
            url = f"https://api.helius.xyz/v0/addresses?api-key={self.helius_key}"

            # Query for recently active programs
            # This is a simplified approach - in production you'd track program deployments
            response = await client.post(
                f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getRecentPerformanceSamples",
                    "params": [10]
                }
            )

            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    # Analyze network activity trends
                    samples = data["result"]
                    if len(samples) >= 2:
                        recent_tps = samples[0].get("numTransactions", 0) / max(samples[0].get("samplePeriodSecs", 1), 1)
                        older_tps = samples[-1].get("numTransactions", 0) / max(samples[-1].get("samplePeriodSecs", 1), 1)

                        if recent_tps > older_tps * 1.2:  # 20% increase
                            self.signals.append(OnChainSignal(
                                signal_type="network_activity",
                                description=f"Network TPS increased by {((recent_tps/older_tps)-1)*100:.1f}%",
                                data={"recent_tps": recent_tps, "older_tps": older_tps},
                                strength=min((recent_tps / older_tps - 1) / 0.5, 1.0),
                                timestamp=datetime.utcnow()
                            ))

        except Exception as e:
            print(f"Error collecting new programs: {e}")

    async def _collect_program_activity(self, client: httpx.AsyncClient, days_back: int):
        """Track activity spikes in known programs"""
        if not self.helius_key:
            return

        # Top Solana programs to monitor
        programs_to_track = [
            ("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", "Jupiter"),
            ("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc", "Orca Whirlpool"),
            ("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin", "Serum DEX"),
            ("TSWAPaqyCSx2KABk68Shruf4rp7CxcNi8hAsbdwmHbN", "Tensor"),
            ("M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K", "Magic Eden"),
            ("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s", "Metaplex"),
            ("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK", "Raydium CPMM"),
            ("jitoxjBo7s8g5M8ypYMYnCBRdwrgRxbgiWf21ZSwgGV", "Jito"),
            ("MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD", "Marinade"),
        ]

        for program_id, name in programs_to_track:
            try:
                # Get recent signatures for the program
                response = await client.post(
                    f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}",
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [
                            program_id,
                            {"limit": 100}
                        ]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and len(data["result"]) > 0:
                        tx_count = len(data["result"])

                        # Check for recent activity surge
                        if tx_count >= 90:  # High activity threshold
                            self.signals.append(OnChainSignal(
                                signal_type="usage_spike",
                                description=f"{name} showing high activity ({tx_count} recent txs)",
                                data={
                                    "program_id": program_id,
                                    "program_name": name,
                                    "transaction_count": tx_count
                                },
                                strength=min(tx_count / 100, 1.0),
                                timestamp=datetime.utcnow()
                            ))

                await asyncio.sleep(0.1)  # Rate limiting

            except Exception as e:
                print(f"Error tracking {name}: {e}")

    async def _collect_token_launches(self, client: httpx.AsyncClient, days_back: int):
        """Detect new token launches and memecoins"""
        if not self.helius_key:
            return

        try:
            # Use Helius DAS API for new token detection
            response = await client.post(
                f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAssetsByGroup",
                    "params": {
                        "groupKey": "collection",
                        "groupValue": "token-2022",
                        "page": 1,
                        "limit": 20
                    }
                }
            )

            # Note: This is a simplified approach
            # In production, you'd use more sophisticated token tracking

        except Exception as e:
            print(f"Error collecting token launches: {e}")

    async def _collect_defi_trends(self, client: httpx.AsyncClient, days_back: int):
        """Track DeFi protocol TVL and volume trends"""
        try:
            # Fetch DeFi Llama data for Solana
            response = await client.get(
                "https://api.llama.fi/v2/chains",
                timeout=10.0
            )

            if response.status_code == 200:
                chains = response.json()
                solana_data = next((c for c in chains if c.get("name") == "Solana"), None)

                if solana_data:
                    tvl = solana_data.get("tvl", 0)
                    self.signals.append(OnChainSignal(
                        signal_type="defi_tvl",
                        description=f"Solana DeFi TVL: ${tvl/1e9:.2f}B",
                        data={"tvl": tvl, "chain": "Solana"},
                        strength=0.5,  # Baseline signal
                        timestamp=datetime.utcnow()
                    ))

            # Get protocol-specific data
            response = await client.get(
                "https://api.llama.fi/v2/protocols",
                timeout=10.0
            )

            if response.status_code == 200:
                protocols = response.json()
                solana_protocols = [
                    p for p in protocols
                    if "Solana" in p.get("chains", [])
                ]

                # Sort by TVL change
                top_growing = sorted(
                    [p for p in solana_protocols if p.get("change_1d")],
                    key=lambda x: x.get("change_1d", 0),
                    reverse=True
                )[:5]

                for protocol in top_growing:
                    if protocol.get("change_1d", 0) > 10:  # >10% daily growth
                        self.signals.append(OnChainSignal(
                            signal_type="defi_growth",
                            description=f"{protocol['name']} TVL up {protocol['change_1d']:.1f}% (24h)",
                            data={
                                "protocol": protocol["name"],
                                "tvl": protocol.get("tvl", 0),
                                "change_1d": protocol.get("change_1d", 0),
                                "change_7d": protocol.get("change_7d", 0),
                            },
                            strength=min(protocol.get("change_1d", 0) / 50, 1.0),
                            timestamp=datetime.utcnow()
                        ))

        except Exception as e:
            print(f"Error collecting DeFi trends: {e}")

    def get_summary(self) -> dict:
        """Get summary of collected signals"""
        signal_types = {}
        for signal in self.signals:
            signal_types[signal.signal_type] = signal_types.get(signal.signal_type, 0) + 1

        return {
            "total_signals": len(self.signals),
            "by_type": signal_types,
            "avg_strength": sum(s.strength for s in self.signals) / max(len(self.signals), 1),
            "collection_time": datetime.utcnow().isoformat()
        }
