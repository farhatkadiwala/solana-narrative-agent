"""
Twitter/X data collector for Solana ecosystem
Tracks KOL discussions, trending topics, and social signals
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
from collections import Counter
from typing import List

from config import config


@dataclass
class TwitterSignal:
    signal_type: str  # "kol_mention", "trending_topic", "viral_tweet", "sentiment_shift"
    description: str
    data: dict
    strength: float  # 0-1
    timestamp: datetime


class TwitterCollector:
    """Collects social signals from Twitter/X"""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self):
        self.bearer_token = config.twitter_bearer_token
        self.signals: List[TwitterSignal] = []
        self.headers = {}
        if self.bearer_token:
            self.headers["Authorization"] = f"Bearer {self.bearer_token}"

    async def collect_all(self, days_back: int = 14) -> List[TwitterSignal]:
        """Collect all Twitter signals for the past N days"""
        self.signals = []

        if not self.bearer_token:
            print("Twitter Bearer Token not set - skipping Twitter collection")
            return self.signals

        async with httpx.AsyncClient(timeout=30.0, headers=self.headers) as client:
            await asyncio.gather(
                self._collect_kol_tweets(client, days_back),
                self._collect_solana_trending(client),
                self._collect_ecosystem_mentions(client, days_back),
                return_exceptions=True
            )

        # Extract topics from collected tweets
        self._extract_trending_topics()

        return self.signals

    async def _collect_kol_tweets(self, client: httpx.AsyncClient, days_back: int):
        """Collect tweets from Solana KOLs"""
        # Build query for KOL tweets about Solana
        kols = config.solana_kols[:10]  # Limit to avoid query length issues

        for kol in kols:
            try:
                # Search tweets from this KOL about Solana topics
                query = f"from:{kol} (solana OR $SOL OR web3 OR defi OR nft)"

                response = await client.get(
                    f"{self.BASE_URL}/tweets/search/recent",
                    params={
                        "query": query,
                        "max_results": 20,
                        "tweet.fields": "public_metrics,created_at,context_annotations",
                        "expansions": "author_id",
                        "user.fields": "public_metrics,verified"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("data", [])

                    for tweet in tweets:
                        metrics = tweet.get("public_metrics", {})
                        engagement = (
                            metrics.get("like_count", 0) +
                            metrics.get("retweet_count", 0) * 2 +
                            metrics.get("reply_count", 0) * 1.5
                        )

                        if engagement >= 50:  # Filter low-engagement tweets
                            self.signals.append(TwitterSignal(
                                signal_type="kol_mention",
                                description=f"@{kol}: {tweet['text'][:100]}...",
                                data={
                                    "author": kol,
                                    "text": tweet["text"],
                                    "tweet_id": tweet["id"],
                                    "likes": metrics.get("like_count", 0),
                                    "retweets": metrics.get("retweet_count", 0),
                                    "replies": metrics.get("reply_count", 0),
                                    "created_at": tweet.get("created_at"),
                                },
                                strength=min(engagement / 1000, 1.0),
                                timestamp=datetime.utcnow()
                            ))

                await asyncio.sleep(1.0)  # Rate limiting

            except Exception as e:
                print(f"Error collecting tweets from {kol}: {e}")

    async def _collect_solana_trending(self, client: httpx.AsyncClient):
        """Find trending Solana-related discussions"""
        trending_queries = [
            "solana -is:retweet lang:en",
            "$SOL -is:retweet lang:en",
            "solana airdrop -is:retweet",
            "solana new protocol -is:retweet",
            "solana alpha -is:retweet",
        ]

        for query in trending_queries:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/tweets/search/recent",
                    params={
                        "query": query,
                        "max_results": 50,
                        "tweet.fields": "public_metrics,created_at",
                        "sort_order": "relevancy"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("data", [])

                    # Find viral tweets
                    for tweet in tweets:
                        metrics = tweet.get("public_metrics", {})
                        engagement = (
                            metrics.get("like_count", 0) +
                            metrics.get("retweet_count", 0) * 2
                        )

                        if engagement >= 200:  # High engagement threshold
                            self.signals.append(TwitterSignal(
                                signal_type="viral_tweet",
                                description=f"Viral: {tweet['text'][:100]}...",
                                data={
                                    "text": tweet["text"],
                                    "tweet_id": tweet["id"],
                                    "likes": metrics.get("like_count", 0),
                                    "retweets": metrics.get("retweet_count", 0),
                                    "query": query,
                                },
                                strength=min(engagement / 2000, 1.0),
                                timestamp=datetime.utcnow()
                            ))

                await asyncio.sleep(1.0)  # Rate limiting

            except Exception as e:
                print(f"Error with query '{query}': {e}")

    async def _collect_ecosystem_mentions(self, client: httpx.AsyncClient, days_back: int):
        """Track mentions of emerging ecosystem projects"""
        # Key projects and protocols to track
        projects = [
            "jupiter solana",
            "marinade finance",
            "jito solana",
            "tensor nft",
            "drip haus",
            "sanctum solana",
            "kamino finance",
            "marginfi",
            "parcl solana",
            "drift protocol",
            "phoenix dex",
            "helium mobile",
            "render network",
            "hivemapper",
        ]

        for project in projects:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/tweets/counts/recent",
                    params={
                        "query": f"{project} -is:retweet",
                        "granularity": "day"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    counts = data.get("data", [])

                    if counts:
                        total_tweets = sum(c.get("tweet_count", 0) for c in counts)
                        # Check for upward trend
                        if len(counts) >= 2:
                            recent = sum(c.get("tweet_count", 0) for c in counts[:3])
                            older = sum(c.get("tweet_count", 0) for c in counts[-3:])

                            if recent > older * 1.3 and total_tweets > 50:  # 30% increase
                                self.signals.append(TwitterSignal(
                                    signal_type="mention_surge",
                                    description=f"'{project}' mentions up {((recent/max(older,1))-1)*100:.0f}%",
                                    data={
                                        "project": project,
                                        "total_mentions": total_tweets,
                                        "recent_mentions": recent,
                                        "older_mentions": older,
                                        "growth_pct": ((recent / max(older, 1)) - 1) * 100
                                    },
                                    strength=min((recent / max(older, 1) - 1) / 2, 1.0),
                                    timestamp=datetime.utcnow()
                                ))

                await asyncio.sleep(1.0)

            except Exception as e:
                print(f"Error tracking {project}: {e}")

    def _extract_trending_topics(self):
        """Extract common topics/hashtags from collected tweets"""
        all_text = " ".join(
            s.data.get("text", "") for s in self.signals
            if s.signal_type in ["kol_mention", "viral_tweet"]
        )

        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', all_text.lower())
        hashtag_counts = Counter(hashtags)

        # Extract @mentions of projects
        mentions = re.findall(r'@(\w+)', all_text.lower())
        mention_counts = Counter(mentions)

        # Add trending hashtags as signals
        for tag, count in hashtag_counts.most_common(10):
            if count >= 3 and tag not in ["solana", "sol", "crypto"]:  # Filter common ones
                self.signals.append(TwitterSignal(
                    signal_type="trending_hashtag",
                    description=f"#{tag} trending ({count} mentions in KOL tweets)",
                    data={
                        "hashtag": tag,
                        "count": count,
                    },
                    strength=min(count / 20, 1.0),
                    timestamp=datetime.utcnow()
                ))

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
