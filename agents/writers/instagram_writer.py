# -*- coding: utf-8 -*-
"""Instagram Content Agent — Visual captions and reel scripts.

Generates Instagram-specific content with:
- Emoji-strategic captions
- Hashtag blocks (10-15)
- Reel scripts under 60 seconds
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.agent_registry import register

INSTAGRAM_PROMPT = """You are JAN, an Instagram content creator for brand '{brand}'.

Write an Instagram caption about: {topic}
Context: {context}

Rules:
- Start with a hook line that stops the scroll
- Use emojis strategically (not every sentence, but meaningful placement)
- Keep the body conversational and relatable
- Include a clear CTA (save this, share with a friend, comment below)
- Add a hashtag block at the very end (10-15 relevant hashtags)
- Keep caption under 150 words (before hashtags)
- Use short paragraphs with line breaks

Output only the caption. No preamble."""


@register
class InstagramWriter(BaseAgent):
    name = "instagram_writer"
    role = "content_creator"
    description = "Creates Instagram captions and reel scripts with emoji strategy and hashtag optimization."
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        topic = kwargs.get("topic", "AI and startups")
        context = kwargs.get("context", kwargs.get("summary", ""))
        plan = kwargs.get("plan", [])

        if plan and not kwargs.get("topic"):
            first = plan[0] if plan else {}
            topic = first.get("title", topic)
            context = first.get("summary", context)

        prompt = INSTAGRAM_PROMPT.format(brand=self.brand, topic=topic, context=context or "No additional context.")

        try:
            from ai_core.llm_router import generate
            draft = generate(prompt=prompt, temperature=0.75, max_tokens=800)
        except Exception as exc:
            self.logger.warning("Instagram generation failed: %s", exc)
            draft = f"[Instagram caption generation failed for: {topic}]"

        return {
            "drafts": [{
                "brand": self.brand,
                "topic": topic,
                "platform": "instagram",
                "content_type": "instagram_caption",
                "draft": draft,
                "llm_generated": True,
                "char_count": len(draft),
            }],
        }

    def format_output(self, data: Any) -> str:
        drafts = data.get("drafts", [])
        if not drafts:
            return "📸 No Instagram captions generated."
        d = drafts[0]
        lines = [f"\n📸 Instagram Caption — {d.get('topic', '')}", ""]
        for line in d.get("draft", "").splitlines():
            lines.append(f"  {line}")
        return "\n".join(lines)
