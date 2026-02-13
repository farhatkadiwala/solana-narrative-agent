"""
FastAPI Web Dashboard for Solana Narrative Detection Agent
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SolanaNarrativeAgent
from config import config


app = FastAPI(
    title="Solana Narrative Detection Agent",
    description="Detect emerging narratives and generate product ideas for the Solana ecosystem",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
agent_state = {
    "agent": SolanaNarrativeAgent(),
    "last_report": None,
    "is_running": False,
    "last_run": None,
    "error": None
}


class RunConfig(BaseModel):
    days_back: int = 14
    ideas_per_narrative: int = 4


@app.get("/")
async def dashboard():
    """Redirect to Next.js frontend"""
    return RedirectResponse(url="http://localhost:3002")


# Legacy HTML kept below for reference - remove after confirming Next.js works
_LEGACY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>solana ideas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #EFEFEF;
            --title: #232323;
            --desc: #7F7F7F;
            --pill-text: #8C8C8C;
            --hero-bg: #292929;
            --hero-border: #1E1E1E;
            --narrative-bg: #F0F0F0;
            --narrative-border: #F7F7F7;
            --footer-bg: #F9F9F9;
            --footer-border: #DEDEDE;
            --green: #008453;
            --link: #008453;
            --divider: #D3D3D3;
        }
        html, body {
            background: var(--bg);
            color: var(--desc);
            font-family: 'Hanken Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 15px;
            line-height: 1.12;
            letter-spacing: -0.75px;
            -webkit-font-smoothing: antialiased;
        }
        [x-cloak] { display: none !important; }
        ::selection { background: var(--green); color: #fff; }

        .shell {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 48px 80px;
            display: flex;
            gap: 32px;
            align-items: flex-start;
        }
        .main { flex: 1; min-width: 0; }

        /* Hero Banner */
        .hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--hero-bg);
            border: 1px solid var(--hero-border);
            border-radius: 6px;
            padding: 20px 40px;
            height: 124px;
            box-shadow: 0 1px 0 0 #000;
            margin-bottom: 32px;
        }
        .hero-left {}
        .hero-sup {
            font-size: 12px;
            font-weight: 400;
            color: rgba(255,255,255,0.5);
            letter-spacing: -0.3px;
            margin-bottom: 2px;
        }
        .hero-title {
            font-size: 28px;
            font-weight: 600;
            color: #fff;
            letter-spacing: -1.4px;
            line-height: 1.1;
        }
        .hero-right {
            text-align: right;
        }
        .hero-timer {
            font-size: 22px;
            font-weight: 600;
            color: rgba(255,255,255,0.85);
            letter-spacing: -0.5px;
            font-variant-numeric: tabular-nums;
        }
        .hero-timer-label {
            font-size: 12px;
            font-weight: 400;
            color: rgba(255,255,255,0.4);
            margin-top: 2px;
        }

        /* Idea list */
        .ideas { display: flex; flex-direction: column; }
        .idea-item {
            padding: 20px 0;
            border-bottom: 1px solid var(--divider);
            position: relative;
        }
        .idea-item:first-child { padding-top: 0; }
        .idea-item:last-child { border-bottom: none; }

        .idea-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
        }
        .idea-title-row {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .idea-title {
            font-size: 19px;
            font-weight: 500;
            color: var(--title);
            letter-spacing: -0.95px;
            line-height: 1;
        }
        .pills { display: flex; flex-wrap: wrap; gap: 6px; }
        .pill {
            font-size: 12px;
            font-weight: 500;
            color: var(--pill-text);
            letter-spacing: -0.24px;
            line-height: 0.93;
            padding: 3px 8px;
            border-radius: 4px;
            background: var(--narrative-bg);
            border: 1px solid var(--narrative-border);
        }

        .copy-icon {
            flex-shrink: 0;
            width: 16px;
            height: 16px;
            cursor: pointer;
            opacity: 0.35;
            transition: opacity .15s;
            margin-top: 3px;
        }
        .copy-icon:hover { opacity: 0.7; }
        .copy-icon.copied { opacity: 1; }

        .idea-pitch {
            font-size: 15px;
            font-weight: 400;
            color: var(--desc);
            letter-spacing: -0.75px;
            line-height: 1.12;
            margin-top: 8px;
        }
        .idea-desc {
            font-size: 15px;
            font-weight: 400;
            color: var(--desc);
            letter-spacing: -0.75px;
            line-height: 1.12;
            margin-top: 6px;
        }
        .idea-desc.collapsed {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .read-toggle {
            font-size: 15px;
            font-weight: 500;
            color: var(--green);
            letter-spacing: -0.75px;
            cursor: pointer;
            margin-top: 4px;
            display: inline-block;
            border: none;
            background: none;
            font-family: inherit;
            padding: 0;
        }
        .read-toggle:hover { text-decoration: underline; }

        /* Bounty links inline */
        .bounties { margin-top: 6px; }
        .bounty-link {
            font-size: 13px;
            font-weight: 500;
            color: var(--green);
            text-decoration: none;
            margin-right: 10px;
        }
        .bounty-link:hover { text-decoration: underline; }

        /* Narratives Sidebar */
        .sidebar {
            width: 320px;
            flex-shrink: 0;
            position: sticky;
            top: 40px;
        }
        .narratives-box {
            background: var(--narrative-bg);
            border: 1px solid var(--narrative-border);
            border-radius: 4px;
            box-shadow: 0 1px 0 0 var(--narrative-border);
            padding: 16px;
        }
        .narratives-title {
            font-size: 17px;
            font-weight: 500;
            color: var(--title);
            letter-spacing: -0.85px;
            line-height: 1;
            margin-bottom: 12px;
        }
        .narrative-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .narrative-pill {
            font-size: 12px;
            font-weight: 500;
            color: var(--pill-text);
            letter-spacing: -0.24px;
            padding: 4px 10px;
            border-radius: 4px;
            background: #E8E8E8;
            border: 1px solid var(--narrative-border);
        }

        /* Analyze button in sidebar */
        .sidebar-actions {
            margin-top: 16px;
        }
        .analyze-btn {
            width: 100%;
            background: var(--hero-bg);
            color: #fff;
            border: none;
            font-size: 14px;
            font-weight: 500;
            font-family: inherit;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            letter-spacing: -0.5px;
            transition: opacity .15s;
        }
        .analyze-btn:hover { opacity: 0.85; }
        .analyze-btn:disabled { opacity: .4; cursor: not-allowed; }
        .sidebar-select {
            width: 100%;
            background: #fff;
            border: 1px solid var(--divider);
            color: var(--title);
            font-size: 13px;
            font-family: inherit;
            padding: 7px 12px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 8px;
            letter-spacing: -0.3px;
        }
        .sidebar-select:focus { outline: none; border-color: var(--green); }

        /* Loading */
        .loading { text-align: center; padding: 80px 0; }
        .loader {
            width: 18px; height: 18px;
            border: 2px solid var(--divider);
            border-top-color: var(--title);
            border-radius: 50%;
            animation: spin .7s linear infinite;
            margin: 0 auto 12px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading p { font-size: 14px; color: var(--desc); }

        /* Empty state */
        .empty { text-align: center; padding: 100px 20px; }
        .empty h2 { font-size: 19px; color: var(--title); font-weight: 500; margin-bottom: 6px; letter-spacing: -0.95px; }
        .empty p { font-size: 15px; color: var(--desc); margin-bottom: 20px; }

        /* Footer */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 38px;
            background: var(--footer-bg);
            border-top: 1px solid var(--footer-border);
            backdrop-filter: blur(62px);
            -webkit-backdrop-filter: blur(62px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 48px;
            z-index: 100;
        }
        .footer-left {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 12px;
            font-weight: 500;
            color: var(--desc);
            letter-spacing: -0.3px;
        }
        .footer-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
        }
        .footer-dot.green { background: var(--green); }
        .footer-dot.red { background: #D34; }
        .footer-status {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .footer-right {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            font-weight: 400;
            color: var(--desc);
            letter-spacing: -0.3px;
        }

        .err { color: #D34; font-size: 13px; }

        @media (max-width: 900px) {
            .shell { flex-direction: column; padding: 24px 20px 80px; }
            .sidebar { width: 100%; position: static; }
        }
    </style>
</head>
<body x-data="app()">
    <div class="shell">
        <div class="main">

            <div class="hero">
                <div class="hero-left">
                    <div class="hero-sup">with the</div>
                    <div class="hero-title">Build while you bear market</div>
                </div>
                <div class="hero-right">
                    <div class="hero-timer" x-text="countdown"></div>
                    <div class="hero-timer-label">Ideas refresh in</div>
                </div>
            </div>

            <div x-show="isRunning" class="loading">
                <div class="loader"></div>
                <p>Collecting signals and generating ideas...</p>
            </div>

            <template x-if="report && !isRunning">
                <div class="ideas">
                    <template x-for="(idea, idx) in report.ideas" :key="idea.id">
                        <div class="idea-item">
                            <div class="idea-header">
                                <div class="idea-title-row">
                                    <span class="idea-title" x-text="idea.title"></span>
                                    <div class="pills">
                                        <span class="pill" x-text="getNarrative(idea.narrative_id)?.category || ''"></span>
                                        <span class="pill" x-text="idea.effort_level"></span>
                                        <template x-if="idea.seeker_compatible">
                                            <span class="pill">Seeker</span>
                                        </template>
                                    </div>
                                </div>
                                <svg class="copy-icon" :class="{ copied: idea._copied }" @click="copyToLLM(idea, idx)" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
                                </svg>
                            </div>

                            <div class="idea-pitch" x-text="idea.elevator_pitch || idea.description.split('.')[0] + '.'"></div>

                            <div class="idea-desc" :class="{ collapsed: !idea._expanded }" x-text="idea.description"></div>

                            <button class="read-toggle" @click="idea._expanded = !idea._expanded" x-text="idea._expanded ? 'Read less' : 'Read more'"></button>

                            <div class="bounties" x-show="idea.bounty_links && idea.bounty_links.length">
                                <template x-for="b in (idea.bounty_links || [])" :key="b.url">
                                    <a class="bounty-link" :href="b.url" target="_blank" x-text="b.title + ' ' + b.prize"></a>
                                </template>
                            </div>
                        </div>
                    </template>
                </div>
            </template>

            <div x-show="!report && !isRunning" class="empty">
                <h2>No ideas yet</h2>
                <p>Run analysis to detect narratives and generate product ideas</p>
            </div>

            <div class="err" x-show="error" x-text="error"></div>

        </div>

        <div class="sidebar">
            <template x-if="report && report.narratives && report.narratives.length">
                <div class="narratives-box">
                    <div class="narratives-title">Narratives this week</div>
                    <div class="narrative-pills">
                        <template x-for="n in report.narratives" :key="n.id">
                            <span class="narrative-pill" x-text="n.category"></span>
                        </template>
                    </div>
                </div>
            </template>
            <div class="sidebar-actions">
                <select class="sidebar-select" x-model="daysBack">
                    <option value="7">7 days</option>
                    <option value="14">14 days</option>
                    <option value="30">30 days</option>
                </select>
                <button class="analyze-btn" @click="runAgent" :disabled="isRunning">
                    <span x-show="!isRunning">Analyze</span>
                    <span x-show="isRunning">Running...</span>
                </button>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="footer-left">
            <div class="footer-status">
                <span class="footer-dot" :class="isRunning ? 'green' : 'green'"></span>
                <span x-text="isRunning ? 'Running' : 'Idle'"></span>
            </div>
            <span x-show="lastRun" x-text="'Updated ' + timeAgo(lastRun)"></span>
        </div>
        <div class="footer-right">
            <span class="footer-dot red"></span>
            <span>Made by an LLM</span>
        </div>
    </div>

    <script>
        function app() {
            return {
                daysBack: 14,
                isRunning: false,
                report: null,
                lastRun: null,
                error: null,
                countdown: '',
                _countdownInterval: null,

                async init() {
                    await this.checkStatus();
                    if (!this.report) await this.loadReport();
                    setInterval(() => this.checkStatus(), 5000);
                    this.startCountdown();
                },

                async loadReport() {
                    try {
                        const res = await fetch('/api/report');
                        if (res.ok) {
                            this.report = await res.json();
                        }
                    } catch (e) {}
                },

                startCountdown() {
                    const update = () => {
                        if (!this.lastRun) {
                            this.countdown = '--:--:--';
                            return;
                        }
                        const last = new Date(this.lastRun).getTime();
                        const next = last + (14 * 24 * 60 * 60 * 1000);
                        const diff = Math.max(0, next - Date.now());
                        const d = Math.floor(diff / 86400000);
                        const h = Math.floor((diff % 86400000) / 3600000);
                        const m = Math.floor((diff % 3600000) / 60000);
                        const s = Math.floor((diff % 60000) / 1000);
                        this.countdown = d + 'd:' + String(h).padStart(2,'0') + 'm:' + String(m).padStart(2,'0') + 's';
                    };
                    update();
                    this._countdownInterval = setInterval(update, 1000);
                },

                async checkStatus() {
                    try {
                        const res = await fetch('/api/status');
                        const data = await res.json();
                        this.isRunning = data.is_running;
                        this.lastRun = data.last_run;
                        if (data.report) this.report = data.report;
                        if (data.error) this.error = data.error;
                    } catch (e) {}
                },

                async runAgent() {
                    this.error = null;
                    this.isRunning = true;
                    try {
                        const res = await fetch('/api/run', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ days_back: parseInt(this.daysBack), ideas_per_narrative: 1 })
                        });
                        const data = await res.json();
                        if (data.error) this.error = data.error;
                    } catch (e) {
                        this.error = e.message;
                    }
                },

                getNarrative(id) {
                    if (!this.report) return null;
                    return this.report.narratives.find(n => n.id === id);
                },

                timeAgo(iso) {
                    if (!iso) return '';
                    const diff = Date.now() - new Date(iso).getTime();
                    const mins = Math.floor(diff / 60000);
                    if (mins < 1) return 'just now';
                    if (mins < 60) return mins + 'm ago';
                    const hrs = Math.floor(mins / 60);
                    if (hrs < 24) return hrs + 'h ago';
                    return Math.floor(hrs / 24) + 'd ago';
                },

                copyToLLM(idea, idx) {
                    const n = this.getNarrative(idea.narrative_id);
                    let text = `# ${idea.title}\\n\\n`;
                    text += `**Elevator Pitch:** ${idea.elevator_pitch || idea.description.split('.')[0] + '.'}\\n\\n`;
                    text += `## What it is\\n${idea.description}\\n\\n`;
                    text += `## Target Users\\n${idea.target_users}\\n\\n`;
                    text += `## Key Features\\n`;
                    (idea.key_features || []).forEach(f => text += `- ${f}\\n`);
                    text += `\\n## Tech Stack\\n${(idea.tech_stack || []).join(', ')}\\n\\n`;
                    text += `## Skills Required\\n${(idea.skills_required || []).join(', ')}\\n\\n`;
                    text += `## Build Guideline\\n${idea.build_guideline || 'N/A'}\\n\\n`;
                    text += `## Competitive Advantage\\n${idea.competitive_advantage}\\n\\n`;
                    text += `## Revenue Model\\n${idea.revenue_model}\\n\\n`;
                    text += `## Effort Level: ${idea.effort_level}\\n`;
                    if (idea.seeker_compatible) text += `\\n## Solana Seeker Mobile\\n${idea.seeker_features}\\n`;
                    if (idea.bounty_links && idea.bounty_links.length) {
                        text += `\\n## Related Bounties\\n`;
                        idea.bounty_links.forEach(b => text += `- [${b.title}](${b.url}) - ${b.prize}\\n`);
                    }
                    if (idea.colosseum_analysis) {
                        const c = idea.colosseum_analysis;
                        text += `\\n## Colosseum Reference\\nSimilar to **${c.reference_project}** (${c.edition}, score: ${c.hackathon_score}) - ${c.insight}\\n`;
                    }
                    if (n) text += `\\n## Narrative Context\\n${n.title} (${n.category}, ${n.trend_direction}, strength: ${(n.strength*100).toFixed(0)}%)\\n${n.summary}\\n`;
                    text += `\\n---\\nHelp me build this. Ask me clarifying questions, then create a detailed technical spec and implementation plan.`;

                    text = text.replace(/\\\\n/g, '\\n');

                    navigator.clipboard.writeText(text).then(() => {
                        idea._copied = true;
                        setTimeout(() => idea._copied = false, 2000);
                    });
                }
            }
        }
    </script>
</body>
</html>
"""


@app.get("/api/status")
async def get_status():
    """Get current agent status"""
    return {
        "is_running": agent_state["is_running"],
        "last_run": agent_state["last_run"],
        "report": agent_state["last_report"],
        "error": agent_state["error"]
    }


@app.post("/api/run")
async def run_agent(config: RunConfig, background_tasks: BackgroundTasks):
    """Start a new analysis run"""
    if agent_state["is_running"]:
        raise HTTPException(status_code=409, detail="Agent is already running")

    agent_state["is_running"] = True
    agent_state["error"] = None

    background_tasks.add_task(
        run_analysis,
        config.days_back,
        config.ideas_per_narrative
    )

    return {"status": "started", "message": "Analysis started in background"}


async def run_analysis(days_back: int, ideas_per_narrative: int):
    """Run the analysis in the background"""
    try:
        agent = SolanaNarrativeAgent()
        report = await agent.run(
            days_back=days_back,
            ideas_per_narrative=ideas_per_narrative
        )

        # Convert to dict for JSON serialization
        from dataclasses import asdict
        report_dict = asdict(report)

        # Handle datetime serialization
        for narrative in report_dict.get("narratives", []):
            if "first_detected" in narrative:
                if hasattr(narrative["first_detected"], "isoformat"):
                    narrative["first_detected"] = narrative["first_detected"].isoformat()

        agent_state["last_report"] = report_dict
        agent_state["last_run"] = datetime.utcnow().isoformat()
        agent_state["error"] = None

        # Save report to file
        agent.save_report("latest_report.json")

    except Exception as e:
        agent_state["error"] = str(e)
        print(f"Analysis error: {e}")
    finally:
        agent_state["is_running"] = False


@app.get("/api/report")
async def get_report():
    """Get the latest report"""
    if not agent_state["last_report"]:
        # Try to load from file
        try:
            with open("latest_report.json") as f:
                agent_state["last_report"] = json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="No report available")

    return agent_state["last_report"]


@app.get("/api/narratives")
async def get_narratives():
    """Get just the narratives from the last report"""
    if not agent_state["last_report"]:
        raise HTTPException(status_code=404, detail="No report available")

    return agent_state["last_report"].get("narratives", [])


@app.get("/api/ideas")
async def get_ideas(effort: Optional[str] = None):
    """Get ideas, optionally filtered by effort level"""
    if not agent_state["last_report"]:
        raise HTTPException(status_code=404, detail="No report available")

    ideas = agent_state["last_report"].get("ideas", [])

    if effort:
        ideas = [i for i in ideas if i.get("effort_level") == effort]

    return ideas


@app.get("/api/config")
async def get_config():
    """Get current configuration status"""
    warnings = config.validate()
    return {
        "llm_provider": config.llm_provider,
        "llm_model": config.llm_model,
        "has_helius": bool(config.helius_api_key),
        "has_github": bool(config.github_token),
        "has_twitter": bool(config.twitter_bearer_token),
        "has_anthropic": bool(config.anthropic_api_key),
        "has_openai": bool(config.openai_api_key),
        "warnings": warnings
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
