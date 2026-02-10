"""
Product Idea Generator
Generates actionable product ideas based on detected narratives
"""
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any, List

import httpx

from config import config
from .narratives import Narrative


@dataclass
class ProductIdea:
    id: str
    narrative_id: str
    title: str
    description: str
    target_users: str
    key_features: List[str]
    tech_stack: List[str]
    competitive_advantage: str
    effort_level: str  # "weekend", "month", "quarter"
    revenue_model: str
    similar_projects: List[str]


class IdeaGenerator:
    """Generates product ideas from detected narratives"""

    def __init__(self):
        self.provider = config.llm_provider
        self.model = config.llm_model
        self.ideas: List[ProductIdea] = []

    async def generate_ideas(self, narratives: List[Narrative], ideas_per_narrative: int = 4) -> List[ProductIdea]:
        """Generate product ideas for each narrative"""
        self.ideas = []

        for narrative in narratives:
            narrative_ideas = await self._generate_for_narrative(narrative, ideas_per_narrative)
            self.ideas.extend(narrative_ideas)

        return self.ideas

    async def _generate_for_narrative(self, narrative: Narrative, count: int) -> List[ProductIdea]:
        """Generate ideas for a single narrative"""

        system_prompt = """You are a product strategist and builder focused on the Solana ecosystem.
Your task is to generate CONCRETE, ACTIONABLE product ideas based on emerging narratives.

For each idea, provide:
1. A clear product concept that can be built
2. Specific features that make it valuable
3. Technical feasibility (what stack to use)
4. Business model

Focus on ideas that are:
- Buildable by a small team or solo developer
- Have clear value proposition
- Leverage Solana's strengths (speed, low fees, composability)
- Not already saturated in the market

Return JSON with this structure:
{
    "ideas": [
        {
            "id": "short-slug-id",
            "title": "Product Name",
            "description": "2-3 sentence product description",
            "target_users": "Who would use this",
            "key_features": ["feature1", "feature2", "feature3"],
            "tech_stack": ["Anchor", "React", "etc"],
            "competitive_advantage": "Why this would win",
            "effort_level": "weekend|month|quarter",
            "revenue_model": "How to monetize",
            "similar_projects": ["existing project 1", "existing project 2"]
        }
    ]
}"""

        user_prompt = f"""Generate {count} product ideas for this emerging Solana narrative:

**Narrative: {narrative.title}**
Category: {narrative.category}
Summary: {narrative.summary}
Trend: {narrative.trend_direction}
Keywords: {', '.join(narrative.keywords)}

Supporting signals:
{json.dumps(narrative.signals, indent=2)}

Generate {count} distinct product ideas that capitalize on this narrative.
Include at least one "weekend project" (simple, quick to build) and one more ambitious idea.
Focus on novel applications, not copies of existing products."""

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
                return self._extract_json(content)
            else:
                print(f"Anthropic API error: {response.status_code}")
                return {"ideas": []}

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
                return {"ideas": []}

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
        """Parse LLM output into ProductIdea objects"""
        ideas = []

        for idx, idea in enumerate(raw_data.get("ideas", [])):
            try:
                product_idea = ProductIdea(
                    id=idea.get("id", f"{narrative_id}-idea-{idx}"),
                    narrative_id=narrative_id,
                    title=idea.get("title", "Untitled"),
                    description=idea.get("description", ""),
                    target_users=idea.get("target_users", ""),
                    key_features=idea.get("key_features", []),
                    tech_stack=idea.get("tech_stack", []),
                    competitive_advantage=idea.get("competitive_advantage", ""),
                    effort_level=idea.get("effort_level", "month"),
                    revenue_model=idea.get("revenue_model", ""),
                    similar_projects=idea.get("similar_projects", [])
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

    def to_dict(self) -> List[dict]:
        """Convert ideas to dictionary format"""
        return [asdict(i) for i in self.ideas]
