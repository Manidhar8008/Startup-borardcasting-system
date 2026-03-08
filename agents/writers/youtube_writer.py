# -*- coding: utf-8 -*-
"""YouTube Script Agent — Video scripts and Shorts.

Generates YouTube-specific content with:
- INTRO / BODY / OUTRO structure
- [B-ROLL] suggestions
- YouTube Shorts (60-second scripts)
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.agent_registry import register

YOUTUBE_PROMPT = """You are JAN, a YouTube scriptwriter for brand '{brand}'.

Write a YouTube video script about: {topic}
Context: {context}

Structure:
INTRO (30 seconds):
- Start with a hook that makes viewers stay
- Preview what they'll learn

BODY (3-4 minutes):
- 3 main points, each with a clear example
- Add [B-ROLL: description] where visual cutaways should go
- Transition between points smoothly

OUTRO (30 seconds):
- Summarize the 3 key takeaways
- CTA: subscribe, like, comment
- Tease next video

Rules:
- Conversational and energetic tone
- Write as spoken language, not formal text
- Total word count: 400-600 words
- Mark B-roll suggestions in [brackets]

Output only the script. No preamble."""


@register
class YouTubeWriter(BaseAgent):
    name = "youtube_writer"
    role = "content_creator"
    description = "Writes YouTube video scripts and Shorts with INTRO/BODY/OUTRO structure and B-ROLL suggestions."
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        topic = kwargs.get("topic", "AI and startups")
        context = kwargs.get("context", kwargs.get("summary", ""))
        plan = kwargs.get("plan", [])

        if plan and not kwargs.get("topic"):
            first = plan[0] if plan else {}
            topic = first.get("title", topic)
            context = first.get("summary", context)

        prompt = YOUTUBE_PROMPT.format(brand=self.brand, topic=topic, context=context or "No additional context.")

        try:
            from ai_core.llm_router import generate
            draft = generate(prompt=prompt, temperature=0.7, max_tokens=1500)
        except Exception as exc:
            self.logger.warning("YouTube generation failed: %s", exc)
            draft = f"[YouTube script generation failed for: {topic}]"

        word_count = len(draft.split())

        return {
            "drafts": [{
                "brand": self.brand,
                "topic": topic,
                "platform": "youtube",
                "content_type": "youtube_script",
                "draft": draft,
                "llm_generated": True,
                "word_count": word_count,
                "estimated_minutes": max(1, word_count // 150),
            }],
        }

    def format_output(self, data: Any) -> str:
        drafts = data.get("drafts", [])
        if not drafts:
            return "🎬 No YouTube scripts generated."
        d = drafts[0]
        lines = [
            f"\n🎬 YouTube Script — {d.get('topic', '')}",
            f"   Words: {d.get('word_count', 0)} | ~{d.get('estimated_minutes', 0)} min",
            "",
        ]
        for line in d.get("draft", "").splitlines():
            lines.append(f"  {line}")
        return "\n".join(lines)
