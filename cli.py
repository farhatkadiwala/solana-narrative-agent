#!/usr/bin/env python3
"""
CLI interface for Solana Narrative Detection Agent
"""
import asyncio
import argparse
import json
import sys
from pathlib import Path

from agent import SolanaNarrativeAgent
from config import config


def main():
    parser = argparse.ArgumentParser(
        description="Solana Narrative Detection Agent - Discover emerging trends and product opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                    # Run full analysis with defaults
  %(prog)s run --days 7           # Analyze past 7 days
  %(prog)s run --output my_report.json
  %(prog)s validate               # Validate configuration
  %(prog)s narratives             # Show cached narratives
  %(prog)s ideas                  # Show cached ideas
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the narrative detection agent")
    run_parser.add_argument(
        "--days", "-d",
        type=int,
        default=14,
        help="Number of days to analyze (default: 14)"
    )
    run_parser.add_argument(
        "--ideas", "-i",
        type=int,
        default=4,
        help="Number of ideas per narrative (default: 4)"
    )
    run_parser.add_argument(
        "--output", "-o",
        type=str,
        default="latest_report.json",
        help="Output file path (default: latest_report.json)"
    )
    run_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted report"
    )

    # Validate command
    subparsers.add_parser("validate", help="Validate configuration")

    # Narratives command
    narratives_parser = subparsers.add_parser("narratives", help="Show narratives from last report")
    narratives_parser.add_argument(
        "--file", "-f",
        type=str,
        default="latest_report.json",
        help="Report file to read"
    )

    # Ideas command
    ideas_parser = subparsers.add_parser("ideas", help="Show ideas from last report")
    ideas_parser.add_argument(
        "--file", "-f",
        type=str,
        default="latest_report.json",
        help="Report file to read"
    )
    ideas_parser.add_argument(
        "--effort", "-e",
        type=str,
        choices=["weekend", "month", "quarter"],
        help="Filter by effort level"
    )

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(run_agent(args))
    elif args.command == "validate":
        validate_config()
    elif args.command == "narratives":
        show_narratives(args)
    elif args.command == "ideas":
        show_ideas(args)
    else:
        parser.print_help()


async def run_agent(args):
    """Run the narrative detection agent"""
    agent = SolanaNarrativeAgent()

    try:
        report = await agent.run(
            days_back=args.days,
            ideas_per_narrative=args.ideas
        )

        if args.json:
            # Output raw JSON
            from dataclasses import asdict
            print(json.dumps(asdict(report), indent=2, default=str))
        else:
            # Print formatted report
            agent.print_report()

        # Save report
        agent.save_report(args.output)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running agent: {e}")
        sys.exit(1)


def validate_config():
    """Validate configuration and show status"""
    print("\n🔧 Configuration Validation")
    print("-" * 40)

    # Check each API
    checks = [
        ("Solana RPC", config.helius_api_key or config.solana_rpc_url != "https://api.mainnet-beta.solana.com"),
        ("GitHub Token", bool(config.github_token)),
        ("Twitter Bearer Token", bool(config.twitter_bearer_token)),
        ("LLM API (OpenRouter)", bool(config.openrouter_api_key)),
        ("LLM API (Anthropic)", bool(config.anthropic_api_key)),
        ("LLM API (OpenAI)", bool(config.openai_api_key)),
    ]

    all_good = True
    for name, status in checks:
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
        if not status and name in ["LLM API (Anthropic)", "LLM API (OpenAI)", "LLM API (OpenRouter)"]:
            pass  # Only need one LLM
        elif not status:
            all_good = False

    # Check if at least one LLM is configured
    if not config.anthropic_api_key and not config.openai_api_key and not config.openrouter_api_key:
        print("\n⚠️  No LLM API configured! Narrative detection will fail.")
        all_good = False

    warnings = config.validate()
    if warnings:
        print("\n⚠️  Warnings:")
        for w in warnings:
            print(f"   - {w}")

    print()
    if all_good:
        print("✅ Configuration looks good!")
    else:
        print("❌ Some configuration issues need attention")

    print("\n💡 Set environment variables or create a .env file:")
    print("   HELIUS_API_KEY=your_key")
    print("   GITHUB_TOKEN=your_token")
    print("   TWITTER_BEARER_TOKEN=your_token")
    print("   ")
    print("   # LLM (choose one):")
    print("   OPENROUTER_API_KEY=your_key  # Recommended")
    print("   LLM_PROVIDER=openrouter")
    print("   LLM_MODEL=anthropic/claude-sonnet-4")


def show_narratives(args):
    """Show narratives from a saved report"""
    try:
        with open(args.file) as f:
            report = json.load(f)

        narratives = report.get("narratives", [])
        if not narratives:
            print("No narratives found in report")
            return

        print(f"\n📊 Narratives from {args.file}")
        print(f"Generated: {report.get('generated_at', 'Unknown')}")
        print("-" * 50)

        for i, n in enumerate(narratives, 1):
            print(f"\n{i}. {n['title']}")
            print(f"   Category: {n['category']}")
            print(f"   Strength: {n['strength']:.2f}")
            print(f"   Trend: {n['trend_direction']}")
            print(f"   {n['summary']}")
            print(f"   Keywords: {', '.join(n.get('keywords', [])[:5])}")

    except FileNotFoundError:
        print(f"Report file not found: {args.file}")
        print("Run 'cli.py run' first to generate a report")
    except json.JSONDecodeError:
        print(f"Invalid JSON in {args.file}")


def show_ideas(args):
    """Show ideas from a saved report"""
    try:
        with open(args.file) as f:
            report = json.load(f)

        ideas = report.get("ideas", [])
        if not ideas:
            print("No ideas found in report")
            return

        # Filter by effort if specified
        if args.effort:
            ideas = [i for i in ideas if i.get("effort_level") == args.effort]

        print(f"\n💡 Product Ideas from {args.file}")
        if args.effort:
            print(f"   Filtered by effort: {args.effort}")
        print("-" * 50)

        # Group by narrative
        narratives = report.get("narratives", [])
        narrative_map = {n["id"]: n["title"] for n in narratives}

        current_narrative = None
        for idea in ideas:
            narrative_id = idea.get("narrative_id")
            if narrative_id != current_narrative:
                current_narrative = narrative_id
                narrative_title = narrative_map.get(narrative_id, "Unknown Narrative")
                print(f"\n📌 {narrative_title}")
                print("-" * 40)

            print(f"\n   {idea['title']} [{idea['effort_level']}]")
            print(f"   {idea['description']}")
            print(f"   Target: {idea.get('target_users', 'N/A')}")
            print(f"   Features: {', '.join(idea.get('key_features', [])[:3])}")
            print(f"   Tech: {', '.join(idea.get('tech_stack', [])[:3])}")
            print(f"   Revenue: {idea.get('revenue_model', 'N/A')}")

    except FileNotFoundError:
        print(f"Report file not found: {args.file}")
        print("Run 'cli.py run' first to generate a report")
    except json.JSONDecodeError:
        print(f"Invalid JSON in {args.file}")


if __name__ == "__main__":
    main()
