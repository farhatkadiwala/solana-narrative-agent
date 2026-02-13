"""
Narrative Detection Engine
Uses LLM to analyze collected signals and identify emerging narratives
"""
import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any, List

import httpx

from config import config


@dataclass
class Narrative:
    id: str
    title: str
    summary: str
    category: str  # defi, nft, gaming, infrastructure, social, ai, depin, payments
    strength: float  # 0-1 based on signal quality and quantity
    signals: List[dict]  # Supporting signals
    keywords: List[str]
    first_detected: datetime
    trend_direction: str  # "emerging", "accelerating", "peaking", "declining"


class NarrativeDetector:
    """Detects and ranks emerging narratives from collected signals"""

    def __init__(self):
        self.provider = config.llm_provider
        self.model = config.llm_model
        self.narratives: List[Narrative] = []

    async def detect_narratives(
        self,
        onchain_signals: list,
        github_signals: list,
        twitter_signals: list
    ) -> List[Narrative]:
        """Analyze all signals and detect narratives"""

        # Prepare signal summaries for LLM
        signal_summary = self._prepare_signal_summary(
            onchain_signals, github_signals, twitter_signals
        )

        # Use LLM to identify narratives
        narratives_raw = await self._llm_detect_narratives(signal_summary)

        # Parse and structure narratives
        self.narratives = self._parse_narratives(
            narratives_raw,
            onchain_signals + github_signals + twitter_signals
        )

        return self.narratives

    def _prepare_signal_summary(
        self,
        onchain_signals: list,
        github_signals: list,
        twitter_signals: list
    ) -> str:
        """Prepare a concise summary of signals for the LLM"""

        sections = []

        # On-chain signals
        if onchain_signals:
            onchain_items = []
            for s in sorted(onchain_signals, key=lambda x: x.strength, reverse=True)[:15]:
                onchain_items.append(f"- [{s.signal_type}] {s.description} (strength: {s.strength:.2f})")
            sections.append("## On-Chain Signals\n" + "\n".join(onchain_items))

        # GitHub signals
        if github_signals:
            github_items = []
            for s in sorted(github_signals, key=lambda x: x.strength, reverse=True)[:15]:
                github_items.append(f"- [{s.signal_type}] {s.description} (strength: {s.strength:.2f})")
            sections.append("## Developer Activity Signals\n" + "\n".join(github_items))

        # Twitter signals
        if twitter_signals:
            twitter_items = []
            for s in sorted(twitter_signals, key=lambda x: x.strength, reverse=True)[:15]:
                twitter_items.append(f"- [{s.signal_type}] {s.description} (strength: {s.strength:.2f})")
            sections.append("## Social/Community Signals\n" + "\n".join(twitter_items))

        return "\n\n".join(sections)

    async def _llm_detect_narratives(self, signal_summary: str) -> dict:
        """Use LLM to detect narratives from signals"""

        system_prompt = """You are an expert crypto analyst specializing in the Solana ecosystem.
Your task is to analyze signals from on-chain data, developer activity, and social media to identify EMERGING NARRATIVES.

Focus on:
1. Novelty - What's NEW and hasn't been widely discussed yet
2. Signal quality - Strong signals from multiple sources
3. Explainability - Clear thesis for why this narrative is emerging
4. Actionability - Potential for building products around this narrative

Categories to consider:
- DeFi (new primitives, yield strategies, derivatives, BNPL, delta-neutral)
- NFTs/Digital Assets (new standards, compressed NFTs, ZK compression use cases)
- Gaming/Entertainment (fully on-chain games, prediction markets, fantasy sports)
- Infrastructure (Firedancer, ZK compression, storage, dev tooling, hardware wallets)
- SocialFi (creator economy, social graphs, identity, time tokenization, retention)
- AI (AI agents, MCP/x402 payments, autonomous trading, LLM+DeFi)
- DePIN (physical infrastructure, IoT, sensors, Seeker mobile hardware)
- Payments/PayFi (stablecoins, remittance, merchant adoption, cross-border, BNPL)
- RWA (real-world assets, tokenized treasuries, equities, institutional adoption)
- Mobile (Solana Seeker apps, dApp Store, PWAs, NFC payments, camera-based apps)

Return your analysis as JSON with this structure:
{
    "narratives": [
        {
            "id": "short-slug-id",
            "title": "Clear, catchy title",
            "summary": "2-3 sentence explanation of the narrative",
            "category": "category from above",
            "strength": 0.0-1.0,
            "keywords": ["keyword1", "keyword2"],
            "trend_direction": "emerging|accelerating|peaking",
            "supporting_evidence": ["evidence1", "evidence2"]
        }
    ]
}

Identify 3-7 distinct narratives, prioritizing quality over quantity."""

        user_prompt = f"""Analyze the following signals from the Solana ecosystem and identify emerging narratives:

{signal_summary}

Based on these signals, what narratives are emerging? Focus on identifying trends that are:
1. New or accelerating (not already mainstream)
2. Supported by multiple signal types (on-chain + social, or dev activity + social)
3. Have clear investment/building thesis

Return your analysis as JSON."""

        try:
            if self.provider == "anthropic":
                return await self._call_anthropic(system_prompt, user_prompt)
            elif self.provider == "openrouter":
                return await self._call_openrouter(system_prompt, user_prompt)
            else:
                return await self._call_openai(system_prompt, user_prompt)
        except Exception as e:
            print(f"LLM error: {e}")
            return {"narratives": []}

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> dict:
        """Call Anthropic Claude API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": config.anthropic_api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "{}")
                # Extract JSON from response
                return self._extract_json(content)
            else:
                print(f"Anthropic API error: {response.status_code} - {response.text}")
                return {"narratives": []}

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> dict:
        """Call OpenAI API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                return json.loads(content)
            else:
                print(f"OpenAI API error: {response.status_code}")
                return {"narratives": []}

    async def _call_openrouter(self, system_prompt: str, user_prompt: str) -> dict:
        """Call OpenRouter API (OpenAI-compatible)"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/solana-narrative-agent",
                    "X-Title": "Solana Narrative Agent"
                },
                json={
                    "model": self.model,
                    "max_tokens": 2000,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                return self._extract_json(content)
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {"narratives": []}

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response"""
        import re

        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()

        try:
            # Try direct parse
            return json.loads(text)
        except:
            pass

        # Try to find JSON block - match the outermost braces
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        # Try greedy match
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        return {"narratives": []}

    def _parse_narratives(self, raw_data: dict, all_signals: list) -> List[Narrative]:
        """Parse LLM output into Narrative objects"""
        narratives = []

        for n in raw_data.get("narratives", []):
            try:
                # Find supporting signals
                keywords = n.get("keywords", [])
                supporting_signals = []

                for signal in all_signals:
                    signal_text = str(signal.data).lower() + signal.description.lower()
                    if any(kw.lower() in signal_text for kw in keywords):
                        supporting_signals.append({
                            "type": signal.signal_type,
                            "description": signal.description,
                            "strength": signal.strength
                        })

                narrative = Narrative(
                    id=n.get("id", f"narrative-{len(narratives)}"),
                    title=n.get("title", "Unknown"),
                    summary=n.get("summary", ""),
                    category=n.get("category", "other"),
                    strength=float(n.get("strength", 0.5)),
                    signals=supporting_signals[:5],  # Limit to 5 signals
                    keywords=keywords,
                    first_detected=datetime.utcnow(),
                    trend_direction=n.get("trend_direction", "emerging")
                )
                narratives.append(narrative)

            except Exception as e:
                print(f"Error parsing narrative: {e}")

        # Sort by strength
        narratives.sort(key=lambda x: x.strength, reverse=True)

        return narratives

    def to_dict(self) -> List[dict]:
        """Convert narratives to dictionary format"""
        return [asdict(n) for n in self.narratives]
