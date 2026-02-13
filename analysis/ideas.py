"""
Product Idea Generator
Generates actionable product ideas based on detected narratives
Enhanced with current Solana ecosystem intelligence (2025-2026)
"""
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any, List, Optional

import httpx

from config import config
from .narratives import Narrative


# ──────────────────────────────────────────────────
# Ideas already on build.superteam.fun — skip these
# unless the angle is genuinely novel
# ──────────────────────────────────────────────────
SUPERTEAM_BUILD_IDEAS = {
    "have i been drained checker", "1-click liquidate portfolio", "1-click mint compressed nfts",
    "better ticketmaster", "ai account parser", "ai evals", "ai web crawlers",
    "ai-powered data labelling", "amm protocol phoenix", "amms sports betting",
    "archain augmented reality", "accept any spl token jupiter", "access crypto without smartphone",
    "ads exchange", "advance trading tools drip", "advanced on-chain ai",
    "aeda wallet", "interactive nft state compression visualizer", "anonymous social networks",
    "apps agents", "arbitrage bot parcl", "archive", "arm the groupchats",
    "automated payment workflows", "automatically offset transactions",
    "autorebalancer lp pools", "bonk arcade", "bitcoin mining micropayments pool",
    "brand vouchers cnfts", "bribe aggregator", "buy now pay later solana pay",
    "buy now pay never", "clamm integration meteora", "card game drip collectibles",
    "chess puzzle app", "coldchain cold-chain logistics", "community-based learning apps",
    "composable nft loyalty", "compressed nfts gaming", "content authenticity",
    "contract method name registry", "corporate bond market solana", "coupon marketplace",
    "creator apps blinks", "creator coins claims", "cross-chain depin index",
    "cross-chain money markets", "cross-chain yield aggregator", "crowdlens content oracle",
    "crypto immigration", "crypto bounties blinks", "crypto credit card",
    "crypto healthcare", "crypto loyalty program", "crypto payroll solution",
    "crypto point of sale depin", "crypto stipend", "crypto tiktok",
    "crypto-powered virtual plant", "cursor perplexity solana", "curve v2",
    "dao voting blinks", "daos risk-pooling vehicles", "data marketplace solana",
    "data provenance ownership", "data-driven drip recommendations", "defi credit score",
    "defi research risk dao", "defi integrations bsol", "defi-powered consumer loans",
    "depin clean energy", "decentralized 23andme", "decentralized ride-hailing",
    "decentralized collectibles marketplace", "decentralized rideshare logistics",
    "decentralized scale ai", "decentralized scraping hub", "decentralized identity dids",
    "decision maker app", "dev tooling environment", "direct ticketing",
    "donation blink", "dust cleaner solana", "e-commerce blinks",
    "egocentric vision data collection", "enabling financial transactions iot",
    "enabling merchants solana pay", "end-to-end payment solutions",
    "enhanced loyalty rewards", "fiat to spl token widget", "fiat-backed stablecoins",
    "finance superapp rwas", "fixed income products", "flatcoins",
    "fractional hardware pools kickstarter machines", "fully on-chain prediction market meteora",
    "fully onchain games", "fully onchain gig economy", "fundraising lsts",
    "futarchy controlled agent", "gpt arbitration", "games token extensions",
    "generative crypto agents", "geo-based gamified apps", "gleanai onboarding engine",
    "global depin phone batteries", "group chat betting", "gumroad solana",
    "habit tracker", "ip infrastructure", "ideas build jito stakenet",
    "identicore decentralized identity physical ai", "idle treasury meteora vaults",
    "improving data querying", "instadapp solana", "intent-based cross-chain dexs",
    "llm prediction markets", "lst options vaults", "lending orderbook",
    "light rpcs", "linkedin friendtech", "liquidating nft any token",
    "live finance trivia", "livephrass wallet", "local bitcoin developing nations",
    "mev-protected swap aggregator", "managing multisigs blinks",
    "market-making scripts openbook", "maybepay", "memecoin blinks",
    "mercor web3 talent", "microlending platform emerging markets",
    "milestone grant manager", "mint web2 data cnfts", "nft standard token extensions",
    "nft-based digital art galleries", "nft-based gaming superapp",
    "negotiation engine orderbooks", "neobanks developing nations",
    "new order types stop loss phoenix", "nioverify scam rug pull detection",
    "no-code point of sale", "no-code tool blinks", "nontine tools pools",
    "novel monetization creators", "offchain underwriting onchain markets",
    "on-chain ev charger map bounties", "onchain cap table", "onchain goal tracker",
    "onchain luxury brands", "onchain mm program phoenix", "onchain moody",
    "onchain self-audit", "one-click depin onboarding kit",
    "one-click telegram bot solana", "one-stop-shop on off-ramp",
    "open market-based scientific publications", "open source dex aggregator",
    "open-grants protocol", "opinion trading blinks", "optimistic orderbook",
    "p2p lending customised interest rate", "p2p payments bordering countries",
    "psu asset tokenization", "pay-per-watt ev charging", "payment widget all tokens",
    "payments nft mints bsol", "permissionless predictions", "perps pair trading",
    "phygital product tiplinks nfc qr", "plugging payments internet",
    "privacy focused stablecoin", "privacy-powered tokenized opinion discovery",
    "private defi", "private onchain identity", "private onchain messaging",
    "product hunt solana", "programmable money", "project walkthroughs",
    "proof-of-clean energy tracker", "proof-of-location",
    "proof-of-location aggregator", "provenance digital assets",
    "pump.fun but for x", "query transactions natural language",
    "rwa collateral lending", "rwa standard token extensions", "read to earn",
    "recruitment skin in game", "regional neobanks", "reputation-based slashing",
    "reusable txn examples custodial wallets", "rug detection api",
    "scan and pay merchants", "search funds", "security analysis tool",
    "shiller slashing", "sign-in with solana", "single token strategy vaults",
    "skilling ecosystem", "smart contract copilot", "smart contract wallet analyzers",
    "social media aggregator", "social media embed solana nfts",
    "social sports betting", "social trust-based p2p onramp", "solana build",
    "solana jobs-to-be-done", "solana loot protocol", "solana nft storage optimizer",
    "solana passport", "solana wallet golf", "sports betting analytics",
    "sports betting exchange", "sports betting market making tools",
    "stablecoin launchpad", "stablecoin p2p marketplaces", "stablecoin clearing house",
    "stablecoins", "stablecoins transfer app", "stablecoins real world payments",
    "streamflow pdf generator", "structured products token extensions",
    "subscriptions streamflow", "superapp blinks", "supply side expression",
    "twap program phoenix", "end of seed phrases", "post claim experience tiplinks",
    "tipping links solana", "tokenization trading", "tokenize personal carbon credits",
    "tokenized assets aggregation", "tokenized ride-sharing reputation",
    "tokenizing creators", "tokenizing precious metals", "tradwi api abstraction",
    "trading tools whales", "transaction guards", "truth chains",
    "tutorial token metadata", "twitch donation chrome extension", "typed accounts",
    "us tokenised stocks", "under-collateralized lending", "universal caller id",
    "unruggable celebcoins", "virtual pet game", "wallet integration meteora dynamic vaults",
    "web2-friendly yield app", "web3 clubhouse", "web3 discord communities",
    "web3 firebase", "web3 gofundme donation matching", "web3 table interface",
    "webapp game tiplink prizes", "webhook service solana pay",
    "wellness crypto apps", "whales defi analytics", "x-to-earn ecosystem",
    "yearly census dashboard", "yield trading protocol", "zk-kyc gateway",
    "composable personal context layer", "consumer crypto ai vibe coding",
    "crvusd", "crypto economic coordination ai agents",
    "embedded ai crypto protocols", "mairket ai defi predictions",
    "revshare protocols solana",
}

# ──────────────────────────────────────────────────
# Colosseum hackathon winners — reference for quality bar
# score = weighted(traction, novelty, solana_fit, team_viability)
# ──────────────────────────────────────────────────
COLOSSEUM_WINNERS = {
    "ore": {"category": "infrastructure", "score": 0.92, "edition": "Renaissance", "desc": "PoW mining on Solana"},
    "reflect": {"category": "defi", "score": 0.95, "edition": "Radar", "desc": "Delta-neutral yield currency, raised $3.75M"},
    "tapedrive": {"category": "infrastructure", "score": 0.93, "edition": "Breakout", "desc": "1400x cheaper on-chain storage"},
    "unruggable": {"category": "infrastructure", "score": 0.94, "edition": "Cypherpunk", "desc": "Hardware wallet, open-source Rust"},
    "supersize": {"category": "gaming", "score": 0.88, "edition": "Radar", "desc": "Fully on-chain multiplayer PvP"},
    "trepa": {"category": "consumer", "score": 0.87, "edition": "Breakout", "desc": "Sentiment prediction mobile app, 2K users"},
    "vanish": {"category": "defi", "score": 0.90, "edition": "Breakout", "desc": "On-chain privacy, shielded pools, raised $1M"},
    "latinum": {"category": "ai", "score": 0.89, "edition": "Breakout", "desc": "MCP payment middleware for AI agents"},
    "capitola": {"category": "consumer", "score": 0.86, "edition": "Cypherpunk", "desc": "Prediction market meta-aggregator"},
    "yumi_finance": {"category": "defi", "score": 0.91, "edition": "Cypherpunk", "desc": "On-chain BNPL, 100+ merchants live"},
    "seer": {"category": "infrastructure", "score": 0.88, "edition": "Cypherpunk", "desc": "Transaction debugger with source maps"},
    "autonom": {"category": "rwa", "score": 0.85, "edition": "Cypherpunk", "desc": "Oracle for RWA dynamic pricing"},
    "mcpay": {"category": "ai", "score": 0.87, "edition": "Cypherpunk", "desc": "MCP + x402 agent payment infra"},
    "pregame": {"category": "consumer", "score": 0.84, "edition": "Radar", "desc": "P2P sports betting"},
    "darklake": {"category": "defi", "score": 0.86, "edition": "Radar", "desc": "ZKP darkpool trading"},
    "greenkwh": {"category": "depin", "score": 0.85, "edition": "Radar", "desc": "Off-grid renewable energy cooperative"},
    "cargobill": {"category": "payments", "score": 0.84, "edition": "Breakout", "desc": "Stablecoin supply chain payments"},
    "lootgo": {"category": "mobile", "score": 0.83, "edition": "Breakout", "desc": "Solana Mobile award winner"},
    "crypto_fantasy_league": {"category": "gaming", "score": 0.82, "edition": "Breakout", "desc": "Fantasy sports for crypto tokens"},
    "alphafc": {"category": "social", "score": 0.83, "edition": "Radar", "desc": "Fan-operated sports team platform"},
}

# ──────────────────────────────────────────────────
# Superteam Earn active bounty categories for matching
# ──────────────────────────────────────────────────
SUPERTEAM_EARN_BOUNTIES = [
    {
        "title": "Audit & Fix Open-Source Solana Repos",
        "url": "https://superteam.fun/earn/listing/fix-open-source-solana-repos-agents",
        "tags": ["security", "smart-contracts", "audit"],
        "prize": "$3,000"
    },
    {
        "title": "Open Innovation Track: Build Anything on Solana",
        "url": "https://superteam.fun/earn/listing/open-innovation-track-agents/",
        "tags": ["development", "open-ended", "ai-agents"],
        "prize": "$5,000"
    },
    {
        "title": "Build Superteam Brazil LMS dApp",
        "url": "https://superteam.fun/earn/listing/superteam-academy/",
        "tags": ["frontend", "education", "nextjs", "gamification"],
        "prize": "$4,800"
    },
    {
        "title": "Build App with FairScale Reputation Infrastructure",
        "url": "https://superteam.fun/earn/listing/fairathon/",
        "tags": ["reputation", "defi", "mainnet", "production"],
        "prize": "$5,000"
    },
    {
        "title": "Cortex Agent Twitter Thread",
        "url": "https://superteam.fun/earn/listing/cortex-agent-twitter/",
        "tags": ["content", "defi", "ai-agents", "trading"],
        "prize": "$3,100"
    },
    {
        "title": "MoMNTum on Solana Research Bounty",
        "url": "https://superteam.fun/earn/listing/superteam-earn-quest-momntum-on-solana-research-bounty/",
        "tags": ["research", "defi", "cefi-defi", "content"],
        "prize": "$1,000"
    },
    {
        "title": "Rust Undead Survivor Challenge",
        "url": "https://superteam.fun/earn/listing/rust-undead-survivor-challenge",
        "tags": ["education", "rust", "content", "gamification"],
        "prize": "$800"
    },
]


def _normalize(text: str) -> str:
    """Normalize text for fuzzy matching against superteam build ideas."""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # remove common filler words
    for w in ["on", "for", "the", "a", "an", "with", "using", "and", "of", "to", "in"]:
        text = re.sub(rf'\b{w}\b', '', text)
    return ' '.join(text.split())


def _is_duplicate_of_superteam(title: str, description: str) -> bool:
    """Check if an idea already exists on build.superteam.fun."""
    norm_title = _normalize(title)
    norm_desc = _normalize(description)
    combined = norm_title + " " + norm_desc

    for existing in SUPERTEAM_BUILD_IDEAS:
        existing_words = set(existing.split())
        # Only flag as duplicate if the title itself is a near-exact match (80%+)
        # Description alone shouldn't trigger — many ideas share domain keywords
        if len(existing_words) >= 2:
            title_overlap = sum(1 for w in existing_words if w in norm_title)
            if title_overlap / len(existing_words) >= 0.8:
                return True
    return False


def _match_bounties(idea_tags: List[str], idea_text: str) -> List[dict]:
    """Match an idea to relevant Superteam Earn bounties."""
    matches = []
    idea_lower = idea_text.lower()
    for bounty in SUPERTEAM_EARN_BOUNTIES:
        tag_overlap = sum(1 for t in bounty["tags"] if t in idea_lower or any(t in tag for tag in idea_tags))
        text_match = sum(1 for word in bounty["title"].lower().split() if word in idea_lower)
        if tag_overlap >= 1 or text_match >= 2:
            matches.append({"title": bounty["title"], "url": bounty["url"], "prize": bounty["prize"]})
    return matches


def _colosseum_score(idea_category: str, idea_text: str) -> Optional[dict]:
    """Score an idea relative to Colosseum hackathon winners in the same category."""
    idea_lower = idea_text.lower()
    best_match = None
    best_score = 0

    for name, data in COLOSSEUM_WINNERS.items():
        # Check category match or description keyword overlap
        cat_match = data["category"] in idea_lower or idea_category.lower() == data["category"]
        desc_words = set(data["desc"].lower().split())
        keyword_match = sum(1 for w in desc_words if w in idea_lower)

        relevance = (0.5 if cat_match else 0) + (keyword_match * 0.1)
        if relevance > best_score and relevance >= 0.3:
            best_score = relevance
            best_match = {
                "reference_project": name,
                "edition": data["edition"],
                "hackathon_score": data["score"],
                "relevance": round(min(relevance, 1.0), 2),
                "insight": data["desc"]
            }

    return best_match


@dataclass
class ProductIdea:
    id: str
    narrative_id: str
    title: str  # 3-4 words max
    elevator_pitch: str  # 1 sentence
    description: str  # <100 words, detailed explanation
    target_users: str
    key_features: List[str]
    tech_stack: List[str]
    competitive_advantage: str
    effort_level: str  # "weekend", "month", "quarter"
    revenue_model: str
    similar_projects: List[str]
    skills_required: List[str]
    build_guideline: str
    bounty_links: List[dict]
    colosseum_analysis: Optional[dict]
    seeker_compatible: bool
    seeker_features: str
    relevant_links: List[dict]  # [{title, url, type}] — tweets, articles, repos relevant to the idea

    def format_for_llm(self) -> str:
        """Format idea as structured text for pasting into any LLM."""
        lines = [
            f"# {self.title}",
            f"",
            f"**Elevator Pitch:** {self.elevator_pitch}",
            f"",
            f"## What it is",
            f"{self.description}",
            f"",
            f"## Target Users",
            f"{self.target_users}",
            f"",
            f"## Key Features",
        ]
        for f in self.key_features:
            lines.append(f"- {f}")
        lines += [
            f"",
            f"## Tech Stack",
            f"{', '.join(self.tech_stack)}",
            f"",
            f"## Skills Required",
            f"{', '.join(self.skills_required)}",
            f"",
            f"## Build Guideline",
            f"{self.build_guideline}",
            f"",
            f"## Competitive Advantage",
            f"{self.competitive_advantage}",
            f"",
            f"## Revenue Model",
            f"{self.revenue_model}",
            f"",
            f"## Effort Level: {self.effort_level}",
        ]
        if self.seeker_compatible:
            lines.append(f"## Solana Seeker Mobile: {self.seeker_features}")
        if self.bounty_links:
            lines.append(f"")
            lines.append(f"## Related Bounties")
            for b in self.bounty_links:
                lines.append(f"- [{b['title']}]({b['url']}) — {b['prize']}")
        if self.colosseum_analysis:
            lines.append(f"")
            lines.append(f"## Colosseum Reference")
            c = self.colosseum_analysis
            lines.append(f"Similar to **{c['reference_project']}** ({c['edition']} hackathon, score: {c['hackathon_score']}) — {c['insight']}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"Help me build this. Ask me clarifying questions, then create a detailed technical spec and implementation plan.")
        return "\n".join(lines)


class IdeaGenerator:
    """Generates product ideas from detected narratives"""

    def __init__(self):
        self.provider = config.llm_provider
        self.model = config.llm_model
        self.ideas: List[ProductIdea] = []

    async def generate_ideas(self, narratives: List[Narrative], ideas_per_narrative: int = 1) -> List[ProductIdea]:
        """Generate the single best idea for each narrative, keep top 5 overall"""
        self.ideas = []

        for narrative in narratives:
            narrative_ideas = await self._generate_for_narrative(narrative, 1)
            self.ideas.extend(narrative_ideas)

        # Rank by parent narrative strength and keep top 5
        narrative_strength = {n.id: n.strength for n in narratives}
        self.ideas.sort(
            key=lambda idea: narrative_strength.get(idea.narrative_id, 0),
            reverse=True
        )
        self.ideas = self.ideas[:5]

        return self.ideas

    async def _generate_for_narrative(self, narrative: Narrative, count: int) -> List[ProductIdea]:
        """Generate ideas for a single narrative"""

        system_prompt = """You are a senior product strategist and Solana ecosystem expert (Feb 2026).
Your job: generate PRECISE, BUILDABLE product ideas that capitalize on CURRENT Solana trends.

=== CURRENT SOLANA ECOSYSTEM CONTEXT (Feb 2026) ===

NETWORK STATE:
- Firedancer live on mainnet (1M+ TPS capability)
- Alpenglow consensus upgrade: ~150ms finality (early 2026)
- ZK Compression on L1: 5000x cheaper state (airdrop 1M users for $50)
- Token Extensions: confidential transfers, interest-bearing, programmable
- Blinks/Actions: embed transactions anywhere (Phantom, Backpack support)

MARKET LEADERS:
- AI Agents: 77% of agent tx volume on Solana ($31B in 2025), $100K hackathon
- RWA: $873M ATH (325% YoY), BlackRock/Ondo treasuries, State Street launching SWEEP
- Stablecoins: $11.7B supply, Western Union building remittance on Solana (H1 2026)
- DePIN: $3.24B market, Helium 1M hotspots, Grass 3M+ users
- PayFi: Huma Finance PayFi Stack, "instant, free, global" money movement

SOLANA SEEKER MOBILE (launched Aug 2025):
- 150,000+ devices shipped, $450-500 price point
- Hardware: 108MP camera, 8GB RAM, 5G, NFC, GPS, 4500mAh battery
- Solana dApp Store: 100+ apps, 0% platform fees, no gatekeepers
- SKR token launched Jan 2026, Genesis Token for exclusive rewards
- PWAs easily convertible to APK for distribution
- KEY OPPORTUNITY: Most apps are DeFi-centric — mainstream consumer apps are MISSING

COLOSSEUM HACKATHON WINNERS (what actually wins):
- Ore: Novel PoW mining mechanism (Renaissance grand prize)
- Reflect: Delta-neutral yield currency like Ethena but on Solana (Radar, raised $3.75M)
- TapeDrive: 1400x cheaper on-chain storage (Breakout)
- Unruggable: Open-source hardware wallet in Rust (Cypherpunk)
- Yumi Finance: On-chain BNPL, 100+ merchants (Cypherpunk)
- Latinum: MCP payment middleware for AI agents (Breakout)
- Seer: Transaction debugger with source maps (Cypherpunk)
- Pattern: Novel primitive + clear use case + Solana-native advantage

KEY OPINIONS FROM ECOSYSTEM LEADERS:
- Mert (Helius): "SocialFi is crypto's biggest opportunity." Stablecoins are "insane no-brainer."
  ZK compression + mobile = massive scale. The bottleneck is useful products, not infra.
- Aditya (Superteam India): Farcaster+Solana integration could add 10K DAU. Mobile-first is underserved.
- Superteam: Instagrants (<48h decision), build.superteam.fun has 271 ideas — we must NOT duplicate.
- Colosseum: Judging prioritizes real problem solving, early traction, founder-market fit.

=== IDEA QUALITY REQUIREMENTS ===

DO NOT generate:
- Generic "trading bot" or "yield aggregator" ideas (saturated)
- Copy of existing well-known projects (Jupiter clone, another DEX, etc.)
- Ideas from 2021-2023 that are stale (basic NFT marketplace, simple wallet, etc.)
- Anything already on build.superteam.fun (271 ideas catalogued)

DO generate:
- Ideas leveraging NEW Solana primitives (ZK compression, token extensions, Blinks, MCP/x402)
- Mobile-first ideas for Seeker (camera, NFC, GPS, sensors)
- AI agent infrastructure and applications (77% market share, growing fast)
- PayFi / stablecoin flows for real-world use (Western Union entering)
- SocialFi with retention mechanics (not another friend.tech clone)
- RWA tokenization with institutional backing (BlackRock, State Street in)
- DePIN leveraging Seeker hardware (camera, location, bandwidth)
- Ideas that could be submitted to Colosseum Eternal or Superteam Earn bounties

STRICT FORMAT RULES:
- "title": EXACTLY 3-4 words. No more.
- "elevator_pitch": EXACTLY 1 sentence. The hook. What it does and why it matters.
- "description": Under 100 words. Explain the mechanism, how it works, what makes it unique.

Generate EXACTLY 1 idea — the single most promising, novel, buildable product for this narrative.

JSON structure:
{
    "ideas": [{
        "id": "short-slug-id",
        "title": "Three Word Name",
        "elevator_pitch": "One sentence that makes someone want to build this.",
        "description": "Under 100 words explaining the mechanism and what makes it unique.",
        "target_users": "Precise user persona, not generic",
        "key_features": ["feature1", "feature2", "feature3"],
        "tech_stack": ["specific framework/tool", "specific SDK/protocol"],
        "competitive_advantage": "What Solana-native advantage makes this possible HERE and not elsewhere",
        "effort_level": "weekend|month|quarter",
        "revenue_model": "Specific monetization, not just 'transaction fees'",
        "similar_projects": ["existing reference 1", "existing reference 2"],
        "skills_required": ["Rust/Anchor smart contracts", "React/Next.js frontend", etc.],
        "build_guideline": "Step-by-step: Week 1 do X, Week 2 do Y... be concrete with milestones",
        "seeker_compatible": true/false,
        "seeker_features": "Which Seeker hardware features it uses (camera, NFC, GPS, etc.) or empty string",
        "relevant_links": [
            {"title": "descriptive title", "url": "https://real-url.com/...", "type": "tweet|article|repo|docs"},
            {"title": "another link", "url": "https://...", "type": "tweet|article|repo|docs"}
        ]
    }]
}

RELEVANT LINKS RULES:
- Include 2-5 links that are DIRECTLY relevant to this specific idea
- Types: "tweet" (X/Twitter posts from KOLs), "article" (blog posts, docs), "repo" (GitHub repos), "docs" (Solana/protocol docs)
- Links MUST be real, verifiable URLs — not made up. Use URLs from the supporting signals when available.
- Good examples: GitHub repos of similar tools, Solana docs for the primitives used, tweets from ecosystem leaders about the problem space
- If you cannot find a real URL, use the relevant Solana documentation page (e.g. https://solana.com/docs, https://spl.solana.com, https://www.helius.dev/blog, https://station.jup.ag/docs)

Return JSON: {"ideas": [...]}"""

        user_prompt = f"""Generate your SINGLE BEST product idea for this Solana narrative:

**Narrative: {narrative.title}**
Category: {narrative.category}
Summary: {narrative.summary}
Trend: {narrative.trend_direction}
Keywords: {', '.join(narrative.keywords)}

Supporting signals:
{json.dumps(narrative.signals, indent=2)}

Give me the ONE idea that is:
- Most novel and differentiated (not on build.superteam.fun)
- Most buildable with a clear path to traction
- Leverages a Solana-native advantage (speed, Blinks, ZK compression, token extensions, Seeker mobile)
- Has a specific user who would pay for it

Title must be 3-4 words. Elevator pitch must be 1 sentence. Description under 100 words.
Include specific build guidelines with weekly milestones and skills needed."""

        try:
            if self.provider == "anthropic":
                result = await self._call_anthropic(system_prompt, user_prompt)
            elif self.provider == "openrouter":
                result = await self._call_openrouter(system_prompt, user_prompt)
            else:
                result = await self._call_openai(system_prompt, user_prompt)

            return self._parse_ideas(result, narrative.id)

        except Exception as e:
            print(f"Error generating ideas for {narrative.title}: {e}")
            return []

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> dict:
        """Call Anthropic Claude API"""
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": config.anthropic_api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 8192,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "{}")
                return self._extract_json(content)
            else:
                print(f"Anthropic API error: {response.status_code}")
                return {"ideas": []}

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> dict:
        """Call OpenAI API"""
        async with httpx.AsyncClient(timeout=90.0) as client:
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
                return {"ideas": []}

    async def _call_openrouter(self, system_prompt: str, user_prompt: str) -> dict:
        """Call OpenRouter API (OpenAI-compatible)"""
        async with httpx.AsyncClient(timeout=180.0) as client:
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
                    "max_tokens": 6000,
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
                return {"ideas": []}

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from LLM response"""
        import re

        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()

        try:
            return json.loads(text)
        except:
            pass

        # Try greedy match
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        return {"ideas": []}

    def _parse_ideas(self, raw_data: dict, narrative_id: str) -> List[ProductIdea]:
        """Parse LLM output into ProductIdea objects, filtering duplicates"""
        ideas = []

        for idx, idea in enumerate(raw_data.get("ideas", [])):
            try:
                title = idea.get("title", "Untitled")
                description = idea.get("description", "")

                # Skip if it duplicates a build.superteam.fun idea
                if _is_duplicate_of_superteam(title, description):
                    print(f"  Skipped duplicate of build.superteam.fun: {title}")
                    continue

                # Compute bounty matches
                idea_text = f"{title} {description} {' '.join(idea.get('key_features', []))}"
                idea_tags = idea.get("tech_stack", []) + idea.get("skills_required", [])
                bounty_matches = _match_bounties(idea_tags, idea_text)

                # Compute Colosseum analysis
                category = idea.get("category", narrative_id.split("-")[0] if "-" in narrative_id else "")
                col_analysis = _colosseum_score(category, idea_text)

                product_idea = ProductIdea(
                    id=idea.get("id", f"{narrative_id}-idea-{idx}"),
                    narrative_id=narrative_id,
                    title=title,
                    elevator_pitch=idea.get("elevator_pitch", ""),
                    description=description,
                    target_users=idea.get("target_users", ""),
                    key_features=idea.get("key_features", []),
                    tech_stack=idea.get("tech_stack", []),
                    competitive_advantage=idea.get("competitive_advantage", ""),
                    effort_level=idea.get("effort_level", "month"),
                    revenue_model=idea.get("revenue_model", ""),
                    similar_projects=idea.get("similar_projects", []),
                    skills_required=idea.get("skills_required", []),
                    build_guideline=idea.get("build_guideline", ""),
                    bounty_links=bounty_matches,
                    colosseum_analysis=col_analysis,
                    seeker_compatible=idea.get("seeker_compatible", False),
                    seeker_features=idea.get("seeker_features", ""),
                    relevant_links=idea.get("relevant_links", []),
                )
                ideas.append(product_idea)
            except Exception as e:
                print(f"Error parsing idea: {e}")

        return ideas

    def get_ideas_by_narrative(self, narrative_id: str) -> List[ProductIdea]:
        """Get all ideas for a specific narrative"""
        return [i for i in self.ideas if i.narrative_id == narrative_id]

    def get_ideas_by_effort(self, effort_level: str) -> List[ProductIdea]:
        """Get ideas filtered by effort level"""
        return [i for i in self.ideas if i.effort_level == effort_level]

    def get_seeker_ideas(self) -> List[ProductIdea]:
        """Get ideas compatible with Solana Seeker mobile"""
        return [i for i in self.ideas if i.seeker_compatible]

    def to_dict(self) -> List[dict]:
        """Convert ideas to dictionary format"""
        return [asdict(i) for i in self.ideas]
