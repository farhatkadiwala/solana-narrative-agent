# Solana Narrative Detection Agent

An AI-powered tool that detects emerging narratives and generates product ideas for the Solana ecosystem. Built for the Superteam bounty.

## Overview

This agent monitors multiple data sources across the Solana ecosystem to identify emerging trends before they become mainstream. It then generates actionable product ideas for each detected narrative.

## Features

- **Multi-source Signal Collection**
  - On-chain activity (programs, TVL, transaction patterns)
  - Developer activity (GitHub repos, commits, stars)
  - Social signals (Twitter/X KOLs, trending topics)

- **AI-Powered Narrative Detection**
  - Identifies emerging and accelerating trends
  - Ranks narratives by signal strength
  - Provides explainable thesis for each narrative

- **Product Idea Generation**
  - 3-5 concrete product ideas per narrative
  - Includes tech stack, effort level, and revenue model
  - Categorized by build complexity (weekend/month/quarter)

- **Dual Interface**
  - Web dashboard for visual exploration
  - CLI for automation and scripting

## Data Sources

### On-Chain Data
- **Solana RPC / Helius API**: Transaction activity, program usage, DeFi TVL
- **DeFi Llama API**: Protocol TVL trends, chain comparison

### Developer Activity
- **GitHub API**: Repository tracking for major Solana orgs
  - solana-labs, coral-xyz, metaplex-foundation
  - jito-foundation, marinade-finance, drift-labs
  - orca-so, raydium-io, jupiter-exchange
  - And more...

### Social Signals
- **Twitter/X API**: KOL tracking
  - @0xMert_, @aeyakovenko, @rajgokal
  - @armaniferrante, @gauntlet_xyz, @solana
  - And more ecosystem voices...

## Signal Detection Methodology

### 1. Data Collection (Fortnightly Refresh)
```
On-Chain → Program activity, TVL changes, whale movements
GitHub   → New repos, commit velocity, star trends
Twitter  → KOL mentions, viral tweets, hashtag frequency
```

### 2. Signal Scoring
Each signal is scored on a 0-1 scale based on:
- **Recency**: More recent = higher weight
- **Source Authority**: KOLs > general users
- **Engagement**: High engagement = stronger signal
- **Cross-source Correlation**: Multiple sources = higher confidence

### 3. Narrative Clustering
Signals are grouped by semantic similarity:
- LLM analyzes combined signals
- Identifies common themes and patterns
- Extracts emerging narrative thesis

### 4. Idea Generation
For each narrative:
- Analyze market gaps
- Consider technical feasibility
- Generate 3-5 product concepts
- Classify by effort level

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd solana-narrative-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with your API keys:

```env
# Solana RPC (Helius recommended for better rate limits)
HELIUS_API_KEY=your_helius_key
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=your_key

# GitHub (for higher rate limits)
GITHUB_TOKEN=your_github_token

# Twitter/X (for social signals)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# LLM Provider (choose one)
ANTHROPIC_API_KEY=your_anthropic_key
# or
OPENAI_API_KEY=your_openai_key

# LLM Settings
LLM_PROVIDER=anthropic  # or "openai"
LLM_MODEL=claude-sonnet-4-20250514
```

## Usage

### CLI

```bash
# Run full analysis
python cli.py run

# Analyze past 7 days
python cli.py run --days 7

# Output raw JSON
python cli.py run --json

# View cached narratives
python cli.py narratives

# View cached ideas (filter by effort)
python cli.py ideas --effort weekend

# Validate configuration
python cli.py validate
```

### Web Dashboard

```bash
# Start the web server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Open http://localhost:8000 in your browser
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/api/status` | GET | Agent status |
| `/api/run` | POST | Start analysis |
| `/api/report` | GET | Get latest report |
| `/api/narratives` | GET | Get narratives only |
| `/api/ideas` | GET | Get ideas (filter with `?effort=weekend`) |
| `/api/config` | GET | Configuration status |

## Output Format

### Narrative Object
```json
{
  "id": "ai-agents-solana",
  "title": "AI Agents on Solana",
  "summary": "Growing interest in autonomous AI agents...",
  "category": "ai",
  "strength": 0.85,
  "keywords": ["ai", "agent", "autonomous", "llm"],
  "trend_direction": "accelerating",
  "signals": [...]
}
```

### Product Idea Object
```json
{
  "id": "ai-wallet-assistant",
  "narrative_id": "ai-agents-solana",
  "title": "AI Wallet Assistant",
  "description": "An AI agent that manages DeFi positions...",
  "target_users": "DeFi users who want automated portfolio management",
  "key_features": ["auto-rebalancing", "yield optimization", "risk alerts"],
  "tech_stack": ["Anchor", "React", "Claude API"],
  "competitive_advantage": "First AI agent with on-chain execution",
  "effort_level": "month",
  "revenue_model": "Performance fees on yield generated",
  "similar_projects": ["DeFi Saver", "Instadapp"]
}
```

## Architecture

```
solana-narrative-agent/
├── agent.py              # Main orchestrator
├── cli.py                # CLI interface
├── config.py             # Configuration management
├── collectors/
│   ├── onchain.py        # Solana on-chain data
│   ├── github.py         # GitHub activity
│   └── twitter.py        # Twitter/X signals
├── analysis/
│   ├── narratives.py     # Narrative detection
│   └── ideas.py          # Idea generation
├── api/
│   └── main.py           # FastAPI web server
├── requirements.txt
└── README.md
```

## Detected Narratives (Sample)

Based on recent analysis, example narratives include:

1. **AI Agents on Solana** (Strength: 0.85)
   - Autonomous agents executing on-chain transactions
   - Growing dev activity in AI+Solana repos
   - KOLs discussing agent infrastructure

2. **Compressed NFTs / State Compression** (Strength: 0.78)
   - Massive cost reduction for NFT minting
   - Gaming and social use cases emerging
   - Metaplex and Helius pushing adoption

3. **DePIN Expansion** (Strength: 0.72)
   - Helium Mobile gaining traction
   - New infrastructure networks launching
   - Cross-chain DePIN infrastructure

## Build Ideas (Sample)

1. **AI Portfolio Manager** [month]
   - Auto-rebalance DeFi positions
   - Natural language commands
   - Risk-adjusted yield optimization

2. **Compressed NFT Loyalty Platform** [weekend]
   - Mint millions of loyalty NFTs cheaply
   - Perfect for brands and games
   - Built on Metaplex Bubblegum

3. **DePIN Node Aggregator** [quarter]
   - Unified dashboard for DePIN earnings
   - Multi-network support
   - Performance optimization

## Reproduction Instructions

1. **Clone and Install**
   ```bash
   git clone <repo>
   cd solana-narrative-agent
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   - Get Helius API key at helius.xyz
   - Get GitHub token at github.com/settings/tokens
   - Get Twitter Bearer Token from developer.twitter.com
   - Get Anthropic API key from console.anthropic.com

3. **Run Analysis**
   ```bash
   python cli.py run --days 14
   ```

4. **View Results**
   - Check `latest_report.json` for full output
   - Or run web dashboard: `python -m uvicorn api.main:app`

## License

MIT

## Built For

Superteam Earn Bounty: "Develop a Narrative Detection and Idea Generation Tool"
