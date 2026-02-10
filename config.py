"""
Configuration management for Solana Narrative Detection Agent
"""
import os
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Solana RPC
    solana_rpc_url: str = field(default_factory=lambda: os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"))
    helius_api_key: Optional[str] = field(default_factory=lambda: os.getenv("HELIUS_API_KEY"))

    # GitHub
    github_token: Optional[str] = field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))

    # Twitter/X
    twitter_bearer_token: Optional[str] = field(default_factory=lambda: os.getenv("TWITTER_BEARER_TOKEN"))

    # LLM
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    openrouter_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openrouter"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4"))

    # Data collection settings
    collection_interval_hours: int = 336  # 14 days (fortnightly)
    max_tweets_per_query: int = 100
    max_repos_per_query: int = 50

    # KOLs to track on Twitter/X
    solana_kols: list = field(default_factory=lambda: [
        "aaboronkov",
        "aaboronkov_sol",
        "0xMert_",
        "aaboronkov",
        "rajgokal",
        "armaboroniux",
        "taboronkov",
        "heaboronkov",
        "solanafloor",
        "solana",
        "SuperteamDAO",
        "heaboronkov",
        "armaniferrante",
        "gaaboronkovntlet",
        "vibhu",
    ])

    # GitHub orgs/users to track
    solana_github_targets: list = field(default_factory=lambda: [
        "solana-labs",
        "coral-xyz",
        "metaplex-foundation",
        "jito-foundation",
        "marinade-finance",
        "drift-labs",
        "orca-so",
        "raydium-io",
        "jupiter-exchange",
        "tensor-hq",
        "magiceden",
        "phantom",
        "solflare-wallet",
        "squads-protocol",
        "pyth-network",
        "switchboard-xyz",
    ])

    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings"""
        warnings = []
        if not self.helius_api_key and self.solana_rpc_url == "https://api.mainnet-beta.solana.com":
            warnings.append("Using public Solana RPC - rate limits apply. Set HELIUS_API_KEY for better performance.")
        if not self.github_token:
            warnings.append("GITHUB_TOKEN not set - rate limits will be restrictive (60 req/hour)")
        if not self.twitter_bearer_token:
            warnings.append("TWITTER_BEARER_TOKEN not set - social signals will be unavailable")
        if not self.openai_api_key and not self.anthropic_api_key and not self.openrouter_api_key:
            warnings.append("No LLM API key set - narrative analysis will fail")
        return warnings


config = Config()
