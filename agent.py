"""
Solana Narrative Detection Agent
Main orchestrator that collects signals, detects narratives, and generates ideas
"""
import asyncio
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional

from collectors import OnChainCollector, GitHubCollector, TwitterCollector
from analysis import NarrativeDetector, IdeaGenerator
from config import config


@dataclass
class AgentReport:
    generated_at: str
    period_days: int
    signal_summary: dict
    narratives: List[dict]
    ideas: List[dict]
    config_warnings: List[str]


class SolanaNarrativeAgent:
    """Main agent that orchestrates the narrative detection pipeline"""

    def __init__(self):
        self.onchain_collector = OnChainCollector()
        self.github_collector = GitHubCollector()
        self.twitter_collector = TwitterCollector()
        self.narrative_detector = NarrativeDetector()
        self.idea_generator = IdeaGenerator()

        self.last_report: Optional[AgentReport] = None

    async def run(self, days_back: int = 14, ideas_per_narrative: int = 4) -> AgentReport:
        """Run the full narrative detection pipeline"""

        print(f"\n{'='*60}")
        print(f"Solana Narrative Detection Agent")
        print(f"Analyzing past {days_back} days...")
        print(f"{'='*60}\n")

        # Validate config
        warnings = config.validate()
        if warnings:
            print("Configuration warnings:")
            for w in warnings:
                print(f"  ⚠️  {w}")
            print()

        # Step 1: Collect signals from all sources
        print("📡 Collecting signals...")

        onchain_signals, github_signals, twitter_signals = await asyncio.gather(
            self._collect_onchain(days_back),
            self._collect_github(days_back),
            self._collect_twitter(days_back),
        )

        signal_summary = {
            "onchain": {
                "count": len(onchain_signals),
                "summary": self.onchain_collector.get_summary()
            },
            "github": {
                "count": len(github_signals),
                "summary": self.github_collector.get_summary()
            },
            "twitter": {
                "count": len(twitter_signals),
                "summary": self.twitter_collector.get_summary()
            },
            "total": len(onchain_signals) + len(github_signals) + len(twitter_signals)
        }

        print(f"\n✅ Collected {signal_summary['total']} signals:")
        print(f"   - On-chain: {len(onchain_signals)}")
        print(f"   - GitHub: {len(github_signals)}")
        print(f"   - Twitter: {len(twitter_signals)}")

        # Step 2: Detect narratives
        print("\n🔍 Detecting narratives...")
        narratives = await self.narrative_detector.detect_narratives(
            onchain_signals, github_signals, twitter_signals
        )

        print(f"\n✅ Detected {len(narratives)} narratives:")
        for n in narratives:
            print(f"   - {n.title} ({n.category}, strength: {n.strength:.2f})")

        # Step 3: Generate product ideas
        print("\n💡 Generating product ideas...")
        ideas = await self.idea_generator.generate_ideas(narratives, ideas_per_narrative)

        print(f"\n✅ Generated {len(ideas)} product ideas")

        # Create report
        self.last_report = AgentReport(
            generated_at=datetime.utcnow().isoformat(),
            period_days=days_back,
            signal_summary=signal_summary,
            narratives=self.narrative_detector.to_dict(),
            ideas=self.idea_generator.to_dict(),
            config_warnings=warnings
        )

        return self.last_report

    async def _collect_onchain(self, days_back: int) -> list:
        """Collect on-chain signals with error handling"""
        try:
            return await self.onchain_collector.collect_all(days_back)
        except Exception as e:
            print(f"Error collecting on-chain signals: {e}")
            return []

    async def _collect_github(self, days_back: int) -> list:
        """Collect GitHub signals with error handling"""
        try:
            return await self.github_collector.collect_all(days_back)
        except Exception as e:
            print(f"Error collecting GitHub signals: {e}")
            return []

    async def _collect_twitter(self, days_back: int) -> list:
        """Collect Twitter signals with error handling"""
        try:
            return await self.twitter_collector.collect_all(days_back)
        except Exception as e:
            print(f"Error collecting Twitter signals: {e}")
            return []

    def save_report(self, filepath: str = "report.json"):
        """Save the last report to a file"""
        if not self.last_report:
            print("No report to save. Run the agent first.")
            return

        # Convert datetime objects for JSON serialization
        report_dict = asdict(self.last_report)

        # Handle datetime serialization in narratives
        for narrative in report_dict.get("narratives", []):
            if "first_detected" in narrative:
                if hasattr(narrative["first_detected"], "isoformat"):
                    narrative["first_detected"] = narrative["first_detected"].isoformat()

        with open(filepath, "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

        print(f"Report saved to {filepath}")

    def print_report(self):
        """Print a formatted report to console"""
        if not self.last_report:
            print("No report available. Run the agent first.")
            return

        print(f"\n{'='*60}")
        print("SOLANA ECOSYSTEM NARRATIVE REPORT")
        print(f"Generated: {self.last_report.generated_at}")
        print(f"Period: Past {self.last_report.period_days} days")
        print(f"{'='*60}\n")

        print("📊 SIGNAL SUMMARY")
        print("-" * 40)
        summary = self.last_report.signal_summary
        print(f"Total signals: {summary['total']}")
        print(f"  • On-chain: {summary['onchain']['count']}")
        print(f"  • GitHub: {summary['github']['count']}")
        print(f"  • Twitter: {summary['twitter']['count']}")

        print(f"\n🔥 EMERGING NARRATIVES ({len(self.last_report.narratives)})")
        print("-" * 40)

        for i, narrative in enumerate(self.last_report.narratives, 1):
            print(f"\n{i}. {narrative['title']}")
            print(f"   Category: {narrative['category']} | Strength: {narrative['strength']:.2f} | Trend: {narrative['trend_direction']}")
            print(f"   {narrative['summary']}")
            print(f"   Keywords: {', '.join(narrative['keywords'][:5])}")

            # Get ideas for this narrative
            narrative_ideas = [
                idea for idea in self.last_report.ideas
                if idea['narrative_id'] == narrative['id']
            ]

            if narrative_ideas:
                print(f"\n   💡 Product Ideas:")
                for j, idea in enumerate(narrative_ideas, 1):
                    print(f"      {j}. {idea['title']} [{idea['effort_level']}]")
                    print(f"         {idea['description'][:100]}...")

        print(f"\n{'='*60}")
        print("END OF REPORT")
        print(f"{'='*60}\n")


async def main():
    """Main entry point"""
    agent = SolanaNarrativeAgent()
    report = await agent.run(days_back=14, ideas_per_narrative=4)
    agent.print_report()
    agent.save_report("latest_report.json")


if __name__ == "__main__":
    asyncio.run(main())
