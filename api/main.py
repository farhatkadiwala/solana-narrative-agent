"""
FastAPI Web Dashboard for Solana Narrative Detection Agent
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
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


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>narratives</title>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "SF Mono", "Fira Code", "Consolas", monospace;
            -webkit-font-smoothing: antialiased;
        }
        :root {
            --bg: #0a0a0a;
            --bg2: #111;
            --bg3: #181818;
            --border: #222;
            --text: #888;
            --text2: #666;
            --text3: #444;
            --white: #ccc;
        }
        html, body { background: var(--bg); color: var(--text); font-size: 11px; line-height: 1.6; }
        [x-cloak] { display: none !important; }
        ::selection { background: #333; color: #fff; }
        a { color: var(--text); text-decoration: none; }
        a:hover { color: var(--white); }

        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }

        header { margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
        header h1 { font-size: 12px; font-weight: 500; color: var(--white); letter-spacing: 0.02em; }
        header p { font-size: 10px; color: var(--text2); margin-top: 4px; }

        .controls { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .control { display: flex; align-items: center; gap: 8px; }
        .control label { font-size: 9px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; }
        select {
            background: var(--bg2);
            border: 1px solid var(--border);
            color: var(--text);
            font-size: 10px;
            padding: 6px 10px;
            cursor: pointer;
            font-family: inherit;
        }
        select:hover { border-color: #333; }
        select:focus { outline: none; border-color: #444; }

        .btn {
            background: var(--bg2);
            border: 1px solid var(--border);
            color: var(--text);
            font-size: 10px;
            padding: 8px 16px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.15s;
        }
        .btn:hover { background: var(--bg3); color: var(--white); border-color: #333; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .btn-primary { background: #1a1a1a; border-color: #333; }

        .status { font-size: 9px; color: var(--text3); margin-bottom: 30px; }
        .status span { margin-right: 15px; }

        .loading { text-align: center; padding: 60px 0; color: var(--text2); }
        .spinner { display: inline-block; width: 12px; height: 12px; border: 1px solid var(--border); border-top-color: var(--text); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 10px; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--border); margin-bottom: 40px; }
        .stat { background: var(--bg); padding: 20px; text-align: center; }
        .stat-value { font-size: 18px; color: var(--white); font-weight: 500; }
        .stat-label { font-size: 9px; color: var(--text3); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em; }

        .section { margin-bottom: 40px; }
        .section-title { font-size: 9px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }

        .narrative { padding: 20px 0; border-bottom: 1px solid var(--border); }
        .narrative:last-child { border-bottom: none; }
        .narrative-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
        .narrative-title { font-size: 12px; color: var(--white); font-weight: 500; }
        .narrative-meta { display: flex; gap: 10px; margin-top: 6px; }
        .narrative-tag { font-size: 9px; color: var(--text2); padding: 2px 6px; background: var(--bg2); }
        .narrative-strength { font-size: 14px; color: var(--text); font-weight: 500; }
        .narrative-summary { font-size: 11px; color: var(--text); line-height: 1.7; margin-bottom: 10px; }
        .narrative-keywords { font-size: 9px; color: var(--text3); }

        .ideas { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }
        .idea { background: var(--bg2); padding: 14px; border: 1px solid var(--border); }
        .idea:hover { border-color: #333; }
        .idea-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 10px; }
        .idea-title { font-size: 10px; color: var(--white); font-weight: 500; }
        .idea-effort { font-size: 8px; color: var(--text3); padding: 2px 5px; background: var(--bg); flex-shrink: 0; }
        .idea-desc { font-size: 10px; color: var(--text2); line-height: 1.6; }

        table { width: 100%; border-collapse: collapse; font-size: 10px; }
        th { text-align: left; font-size: 9px; color: var(--text3); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; padding: 10px 0; border-bottom: 1px solid var(--border); }
        td { padding: 12px 0; border-bottom: 1px solid var(--border); color: var(--text); vertical-align: top; }
        td:first-child { color: var(--white); font-weight: 500; }
        tr:hover td { background: var(--bg2); }

        .empty { text-align: center; padding: 80px 20px; }
        .empty-title { font-size: 12px; color: var(--text); margin-bottom: 8px; }
        .empty-desc { font-size: 10px; color: var(--text3); margin-bottom: 20px; }

        footer { text-align: center; padding: 40px 0; font-size: 9px; color: var(--text3); border-top: 1px solid var(--border); }
    </style>
</head>
<body x-data="app()">
    <div class="container">

        <header>
            <h1>solana narrative agent</h1>
            <p>emerging trends · product opportunities</p>
        </header>

        <div class="controls">
            <div class="control">
                <label>period</label>
                <select x-model="daysBack">
                    <option value="7">7d</option>
                    <option value="14">14d</option>
                    <option value="30">30d</option>
                </select>
            </div>
            <div class="control">
                <label>ideas</label>
                <select x-model="ideasPerNarrative">
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                </select>
            </div>
            <div class="control">
                <label>auto</label>
                <select x-model="autoRefreshInterval" @change="setupAutoRefresh()">
                    <option value="0">off</option>
                    <option value="1">1h</option>
                    <option value="6">6h</option>
                    <option value="12">12h</option>
                    <option value="24">24h</option>
                </select>
            </div>
            <button class="btn btn-primary" @click="runAgent" :disabled="isRunning" style="margin-left: auto;">
                <span x-show="!isRunning">run</span>
                <span x-show="isRunning">running...</span>
            </button>
        </div>

        <div class="status">
            <span x-show="lastRun">last: <span x-text="lastRun"></span></span>
            <span x-show="nextRefresh" x-text="getCountdown()"></span>
            <span x-show="error" style="color: #a55;" x-text="error"></span>
        </div>

        <div x-show="isRunning" class="loading">
            <div class="spinner"></div>
            <p>collecting signals...</p>
        </div>

        <template x-if="report && !isRunning">
            <div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value" x-text="report.signal_summary.total"></div>
                        <div class="stat-label">total</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" x-text="report.signal_summary.onchain.count"></div>
                        <div class="stat-label">onchain</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" x-text="report.signal_summary.github.count"></div>
                        <div class="stat-label">github</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" x-text="report.signal_summary.twitter.count"></div>
                        <div class="stat-label">twitter</div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">narratives</div>
                    <template x-for="narrative in report.narratives" :key="narrative.id">
                        <div class="narrative">
                            <div class="narrative-header">
                                <div>
                                    <div class="narrative-title" x-text="narrative.title"></div>
                                    <div class="narrative-meta">
                                        <span class="narrative-tag" x-text="narrative.category"></span>
                                        <span class="narrative-tag" x-text="narrative.trend_direction"></span>
                                    </div>
                                </div>
                                <div class="narrative-strength" x-text="(narrative.strength * 100).toFixed(0) + '%'"></div>
                            </div>
                            <p class="narrative-summary" x-text="narrative.summary"></p>
                            <div class="narrative-keywords" x-text="narrative.keywords.slice(0, 5).join(' · ')"></div>

                            <div class="ideas">
                                <template x-for="idea in getIdeasForNarrative(narrative.id)" :key="idea.id">
                                    <div class="idea">
                                        <div class="idea-header">
                                            <span class="idea-title" x-text="idea.title"></span>
                                            <span class="idea-effort" x-text="idea.effort_level"></span>
                                        </div>
                                        <p class="idea-desc" x-text="idea.description.substring(0, 100) + '...'"></p>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </template>
                </div>

                <div class="section">
                    <div class="section-title">all ideas</div>
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 25%">title</th>
                                <th style="width: 30%">target</th>
                                <th style="width: 10%">effort</th>
                                <th style="width: 35%">revenue</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template x-for="idea in report.ideas" :key="idea.id">
                                <tr>
                                    <td x-text="idea.title"></td>
                                    <td x-text="idea.target_users"></td>
                                    <td x-text="idea.effort_level"></td>
                                    <td x-text="idea.revenue_model"></td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </div>
        </template>

        <div x-show="!report && !isRunning" class="empty">
            <div class="empty-title">no analysis yet</div>
            <div class="empty-desc">run analysis to detect emerging narratives</div>
            <button class="btn" @click="runAgent">run</button>
        </div>

    </div>

    <footer>solana narrative agent</footer>

    <script>
        function app() {
            return {
                daysBack: 14,
                ideasPerNarrative: 4,
                isRunning: false,
                report: null,
                lastRun: null,
                error: null,
                autoRefreshInterval: 0,
                autoRefreshTimer: null,
                nextRefresh: null,

                async init() {
                    await this.checkStatus();
                    // Poll for status updates every 5 seconds
                    setInterval(() => this.checkStatus(), 5000);
                    // Update countdown every second
                    setInterval(() => this.updateCountdown(), 1000);
                },

                async checkStatus() {
                    try {
                        const res = await fetch('/api/status');
                        const data = await res.json();
                        this.isRunning = data.is_running;
                        this.lastRun = data.last_run;
                        if (data.report) {
                            this.report = data.report;
                        }
                        if (data.error) {
                            this.error = data.error;
                        }
                    } catch (e) {
                        console.error('Status check failed:', e);
                    }
                },

                setupAutoRefresh() {
                    if (this.autoRefreshTimer) {
                        clearInterval(this.autoRefreshTimer);
                        this.autoRefreshTimer = null;
                    }

                    const hours = parseInt(this.autoRefreshInterval);
                    if (hours > 0) {
                        const ms = hours * 60 * 60 * 1000;
                        this.nextRefresh = Date.now() + ms;
                        this.autoRefreshTimer = setInterval(() => {
                            if (!this.isRunning) {
                                this.runAgent();
                                this.nextRefresh = Date.now() + ms;
                            }
                        }, ms);
                    } else {
                        this.nextRefresh = null;
                    }
                },

                updateCountdown() {
                    // This just triggers reactivity for the countdown display
                },

                getCountdown() {
                    if (!this.nextRefresh) return '';
                    const diff = this.nextRefresh - Date.now();
                    if (diff <= 0) return 'Running soon...';
                    const hours = Math.floor(diff / 3600000);
                    const mins = Math.floor((diff % 3600000) / 60000);
                    const secs = Math.floor((diff % 60000) / 1000);
                    return `Next run in ${hours}h ${mins}m ${secs}s`;
                },

                async runAgent() {
                    this.error = null;
                    this.isRunning = true;
                    try {
                        const res = await fetch('/api/run', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                days_back: parseInt(this.daysBack),
                                ideas_per_narrative: parseInt(this.ideasPerNarrative)
                            })
                        });
                        const data = await res.json();
                        if (data.error) {
                            this.error = data.error;
                        }
                    } catch (e) {
                        this.error = 'Failed to start analysis: ' + e.message;
                    }
                },

                getIdeasForNarrative(narrativeId) {
                    if (!this.report || !this.report.ideas) return [];
                    return this.report.ideas.filter(i => i.narrative_id === narrativeId);
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
