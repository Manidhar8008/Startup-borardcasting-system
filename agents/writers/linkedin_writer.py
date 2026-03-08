# -*- coding: utf-8 -*-
"""LinkedIn Writer Agent — Professional thought leadership posts.

Generates LinkedIn-specific content with:
- Professional but human tone
- Hook / Insight / Example / CTA structure
- Hashtag optimization
- Character limit awareness (3000 chars)
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.agent_registry import register

LINKEDIN_PROMPT = """You are JAN, a LinkedIn content strategist for brand '{brand}'.

Write a LinkedIn post about: {topic}
Context: {context}

Rules:
- Professional but human, conversational tone
- Use line breaks generously for readability
- Start with a powerful hook (question, statistic, or bold statement)
- Deliver one clear insight with a real example
- End with a call to action that invites comments
- Add 3-5 relevant hashtags at the end
- Keep under 200 words
- Never use generic platitudes

Structure:
Hook: <attention-grabbing opening>
Insight: <the core valuable idea>
Example: <concrete real-world proof>
CTA: <engage the reader>

Output only the post text. No labels, no preamble."""


@register
class LinkedInWriter(BaseAgent):
    name = "linkedin_writer"
    role = "content_creator"
    description = "Writes LinkedIn thought leadership posts with professional tone and engagement-optimized structure."
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        topic = kwargs.get("topic", "AI and startups")
        context = kwargs.get("context", kwargs.get("summary", ""))
        plan = kwargs.get("plan", [])

        # If given a plan list, use the first item
        if plan and not topic:
            first = plan[0] if plan else {}
            topic = first.get("title", topic)
            context = first.get("summary", context)

        prompt = LINKEDIN_PROMPT.format(brand=self.brand, topic=topic, context=context or "No additional context.")

        try:
            from ai_core.llm_router import generate
            draft = generate(prompt=prompt, temperature=0.7, max_tokens=1000)
        except Exception as exc:
            self.logger.warning("LinkedIn generation failed: %s", exc)
            draft = f"[LinkedIn draft generation failed for: {topic}]"

        # Platform-optimize
        try:
            from network_engine.content_transformer import generate_linkedin_post
            transformed = generate_linkedin_post(draft, brand=self.brand)
            final_text = transformed.get("text", draft)
        except Exception:
            final_text = draft

        return {
            "drafts": [{
                "brand": self.brand,
                "topic": topic,
                "platform": "linkedin",
                "content_type": "linkedin_post",
                "draft": final_text,
                "llm_generated": True,
                "char_count": len(final_text),
            }],
        }

    def format_output(self, data: Any) -> str:
        drafts = data.get("drafts", [])
        if not drafts:
            return "📝 No LinkedIn drafts generated."
        d = drafts[0]
        lines = [
            f"\n📝 LinkedIn Post — {d.get('topic', '')}",
            f"   Characters: {d.get('char_count', 0)}",
            "",
        ]
        for line in d.get("draft", "").splitlines():
            lines.append(f"  {line}")
        return "\n".join(lines)
