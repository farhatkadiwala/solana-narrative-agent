"""
GitHub data collector for Solana ecosystem
Tracks developer activity, new repos, commits, and trending projects
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List

from config import config


@dataclass
class GitHubSignal:
    signal_type: str  # "new_repo", "activity_spike", "trending", "major_release"
    description: str
    data: dict
    strength: float  # 0-1
    timestamp: datetime


class GitHubCollector:
    """Collects developer activity signals from GitHub"""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = config.github_token
        self.signals: List[GitHubSignal] = []
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def collect_all(self, days_back: int = 14) -> List[GitHubSignal]:
        """Collect all GitHub signals for the past N days"""
        self.signals = []
        since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"

        async with httpx.AsyncClient(timeout=30.0, headers=self.headers) as client:
            # Run collectors concurrently
            await asyncio.gather(
                self._collect_trending_repos(client),
                self._collect_org_activity(client, since_date),
                self._collect_solana_search(client, since_date),
                self._collect_new_solana_repos(client, since_date),
                return_exceptions=True
            )

        return self.signals

    async def _collect_trending_repos(self, client: httpx.AsyncClient):
        """Find trending Solana-related repositories"""
        try:
            # Search for recently created Solana repos with stars
            response = await client.get(
                f"{self.BASE_URL}/search/repositories",
                params={
                    "q": "solana created:>2025-01-01 stars:>10",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 30
                }
            )

            if response.status_code == 200:
                data = response.json()
                for repo in data.get("items", [])[:15]:
                    stars = repo.get("stargazers_count", 0)
                    forks = repo.get("forks_count", 0)

                    # Calculate signal strength based on engagement
                    strength = min((stars + forks * 2) / 200, 1.0)

                    if strength > 0.1:  # Filter low-signal repos
                        self.signals.append(GitHubSignal(
                            signal_type="trending",
                            description=f"Trending: {repo['full_name']} ({stars} stars)",
                            data={
                                "repo": repo["full_name"],
                                "url": repo["html_url"],
                                "description": repo.get("description", ""),
                                "stars": stars,
                                "forks": forks,
                                "language": repo.get("language"),
                                "topics": repo.get("topics", []),
                                "created_at": repo.get("created_at"),
                            },
                            strength=strength,
                            timestamp=datetime.utcnow()
                        ))

        except Exception as e:
            print(f"Error collecting trending repos: {e}")

    async def _collect_org_activity(self, client: httpx.AsyncClient, since_date: str):
        """Track activity from major Solana ecosystem orgs"""
        for org in config.solana_github_targets[:10]:  # Limit to avoid rate limits
            try:
                # Get recent repos
                response = await client.get(
                    f"{self.BASE_URL}/orgs/{org}/repos",
                    params={
                        "sort": "pushed",
                        "direction": "desc",
                        "per_page": 10
                    }
                )

                if response.status_code == 200:
                    repos = response.json()
                    for repo in repos[:5]:
                        pushed_at = repo.get("pushed_at", "")
                        if pushed_at >= since_date:
                            # Get recent commits
                            commits_resp = await client.get(
                                f"{self.BASE_URL}/repos/{org}/{repo['name']}/commits",
                                params={"since": since_date, "per_page": 10}
                            )

                            commit_count = 0
                            if commits_resp.status_code == 200:
                                commit_count = len(commits_resp.json())

                            if commit_count >= 5:  # Active development
                                self.signals.append(GitHubSignal(
                                    signal_type="activity_spike",
                                    description=f"{org}/{repo['name']}: {commit_count} commits recently",
                                    data={
                                        "org": org,
                                        "repo": repo["name"],
                                        "full_name": repo["full_name"],
                                        "url": repo["html_url"],
                                        "commit_count": commit_count,
                                        "description": repo.get("description", ""),
                                        "stars": repo.get("stargazers_count", 0),
                                    },
                                    strength=min(commit_count / 20, 1.0),
                                    timestamp=datetime.utcnow()
                                ))

                await asyncio.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"Error collecting org {org}: {e}")

    async def _collect_solana_search(self, client: httpx.AsyncClient, since_date: str):
        """Search for emerging Solana topics and technologies"""
        search_topics = [
            "solana blink",
            "solana actions",
            "solana compressed nft",
            "solana token extensions",
            "solana mobile",
            "solana ai agent",
            "solana mev",
            "solana depin",
            "anchor solana",
        ]

        for topic in search_topics:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/search/repositories",
                    params={
                        "q": f"{topic} pushed:>2025-01-01",
                        "sort": "updated",
                        "order": "desc",
                        "per_page": 5
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    total_count = data.get("total_count", 0)

                    if total_count > 5:  # Topic has activity
                        top_repo = data.get("items", [{}])[0] if data.get("items") else {}
                        self.signals.append(GitHubSignal(
                            signal_type="topic_trend",
                            description=f"Topic '{topic}': {total_count} active repos",
                            data={
                                "topic": topic,
                                "repo_count": total_count,
                                "top_repo": top_repo.get("full_name"),
                                "top_repo_url": top_repo.get("html_url"),
                                "top_repo_stars": top_repo.get("stargazers_count", 0),
                            },
                            strength=min(total_count / 50, 1.0),
                            timestamp=datetime.utcnow()
                        ))

                await asyncio.sleep(1.0)  # Rate limiting for search API

            except Exception as e:
                print(f"Error searching topic {topic}: {e}")

    async def _collect_new_solana_repos(self, client: httpx.AsyncClient, since_date: str):
        """Find newly created Solana repositories"""
        try:
            response = await client.get(
                f"{self.BASE_URL}/search/repositories",
                params={
                    "q": f"solana created:>{since_date[:10]}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 20
                }
            )

            if response.status_code == 200:
                data = response.json()
                new_repos = data.get("items", [])

                for repo in new_repos:
                    stars = repo.get("stargazers_count", 0)
                    if stars >= 5:  # Filter noise
                        self.signals.append(GitHubSignal(
                            signal_type="new_repo",
                            description=f"New repo: {repo['full_name']} ({stars} stars in first days)",
                            data={
                                "repo": repo["full_name"],
                                "url": repo["html_url"],
                                "description": repo.get("description", ""),
                                "stars": stars,
                                "language": repo.get("language"),
                                "topics": repo.get("topics", []),
                                "created_at": repo.get("created_at"),
                            },
                            strength=min(stars / 50, 1.0),
                            timestamp=datetime.utcnow()
                        ))

        except Exception as e:
            print(f"Error collecting new repos: {e}")

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
