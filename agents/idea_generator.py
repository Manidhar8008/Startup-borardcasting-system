# -*- coding: utf-8 -*-
"""Idea Generator Agent — Converts ranked topics into content angles and ideas.

Takes ranked topics and generates:
  - Content angles for each topic
  - Post ideas (LinkedIn, Twitter, Instagram)
  - Video ideas (YouTube, Shorts)
  - Podcast ideas
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register

IDEA_PROMPT = """You are JAN, a content strategist for brand '{brand}'.

For the topic: {topic}
Context: {context}

Generate content ideas in these categories:

POST IDEAS (3):
- <LinkedIn/Twitter post idea with angle>

VIDEO IDEAS (2):
- <YouTube video idea with hook>

PODCAST IDEAS (1):
- <Podcast episode idea>

CONTENT ANGLES (3):
- <unique angle or perspective on this topic>

Rules:
- Each idea must be specific and actionable, not generic
- Include the hook or angle, not just the topic
- Think like a creator who needs to stand out

Output ONLY the ideas in the format above. No preamble."""


def _parse_ideas(raw: str, topic: str) -> Dict:
    """Parse LLM output into structured idea categories."""
    categories: Dict[str, List[str]] = {
        "post_ideas": [], "video_ideas": [], "podcast_ideas": [], "content_angles": [],
    }
    current_key = None

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        upper = line.upper()
        if "POST IDEAS" in upper:
            current_key = "post_ideas"
        elif "VIDEO IDEAS" in upper:
            current_key = "video_ideas"
        elif "PODCAST IDEAS" in upper:
            current_key = "podcast_ideas"
        elif "CONTENT ANGLES" in upper:
            current_key = "content_angles"
        elif line.startswith("- ") and current_key:
            categories[current_key].append(line[2:].strip())

    return {
        "topic": topic,
        **categories,
        "total_ideas": sum(len(v) for v in categories.values()),
    }


@register
class IdeaGenerator(BaseAgent):
    name = "idea_generator"
    role = "idea_intelligence"
    description = (
        "Converts ranked topics into content angles, post ideas, "
        "video ideas, and podcast ideas using Gemini."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Generate ideas from ranked topics.

        Expected kwargs:
            ranked_topics (list): From TopicRanker.
            topic (str): Single topic override.
            count (int): How many topics to process (default: 3).

        Returns:
            Dict with 'idea_feed' list.
        """
        topics = kwargs.get("ranked_topics", [])
        single = kwargs.get("topic", "")
        count = kwargs.get("count", 3)

        if single and not topics:
            topics = [{"topic": single, "summary": ""}]

        if not topics:
            return {"idea_feed": [], "error": "No topics to generate ideas for."}

        idea_feed = []
        for topic_dict in topics[:count]:
            topic_name = topic_dict.get("topic", topic_dict.get("title", ""))
            context = topic_dict.get("summary", "")

            prompt = IDEA_PROMPT.format(
                brand=self.brand, topic=topic_name, context=context or "No extra context."
            )

            try:
                from ai_core.llm_router import generate
                raw = generate(prompt=prompt, temperature=0.8, max_tokens=800)
                ideas = _parse_ideas(raw, topic_name)
            except Exception as exc:
                self.logger.warning("Idea generation failed for '%s': %s", topic_name, exc)
                ideas = {
                    "topic": topic_name,
                    "post_ideas": [f"Write about {topic_name}"],
                    "video_ideas": [f"Explain {topic_name}"],
                    "podcast_ideas": [],
                    "content_angles": [],
                    "total_ideas": 2,
                }

            ideas["rank_score"] = topic_dict.get("rank_score", 0)
            idea_feed.append(ideas)

        return {
            "idea_feed": idea_feed,
            "total_topics": len(idea_feed),
            "total_ideas": sum(i.get("total_ideas", 0) for i in idea_feed),
        }

    def format_output(self, data: Any) -> str:
        feed = data.get("idea_feed", [])
        if not feed:
            return "💡 No ideas generated."

        lines = [f"\n💡 Idea Feed — {data.get('total_ideas', 0)} ideas across {len(feed)} topics"]

        for entry in feed:
            lines.append(f"\n  📌 {entry.get('topic', '?')} (score: {entry.get('rank_score', 0):.2f})")

            if entry.get("post_ideas"):
                lines.append("     📝 Posts:")
                for idea in entry["post_ideas"]:
                    lines.append(f"        • {idea}")

            if entry.get("video_ideas"):
                lines.append("     🎬 Videos:")
                for idea in entry["video_ideas"]:
                    lines.append(f"        • {idea}")

            if entry.get("podcast_ideas"):
                lines.append("     🎙️ Podcast:")
                for idea in entry["podcast_ideas"]:
                    lines.append(f"        • {idea}")

            if entry.get("content_angles"):
                lines.append("     🔍 Angles:")
                for angle in entry["content_angles"]:
                    lines.append(f"        • {angle}")

        return "\n".join(lines)
