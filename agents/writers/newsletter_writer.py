# -*- coding: utf-8 -*-
"""Newsletter Writer Agent — Email-ready content sections.

Generates newsletter content with:
- Subject line optimization
- Preview text
- Scannable body format
- CTA with link placeholders
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.agent_registry import register

NEWSLETTER_PROMPT = """You are JAN, a newsletter writer for brand '{brand}'.

Write a newsletter section about: {topic}
Context: {context}

Structure:
SUBJECT: <compelling subject line, under 60 chars>
PREVIEW: <preview text for email clients, under 100 chars>

LEAD: <opening paragraph that hooks the reader>

KEY POINTS:
- <bullet 1 — the most important insight>
- <bullet 2 — supporting data or example>
- <bullet 3 — actionable takeaway>

TIP: <one actionable tip the reader can apply today>

CTA: <call to action with [link placeholder]>

Rules:
- Scannable format: short paragraphs, bullet points
- Under 300 words total
- Personal, conversational tone (like writing to a friend)
- Value-first: teach something useful
- One clear CTA only

Output only the newsletter content. No preamble."""


@register
class NewsletterWriter(BaseAgent):
    name = "newsletter_writer"
    role = "content_creator"
    description = "Creates email newsletters with subject line optimization, scannable format, and engagement-optimized CTAs."
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        topic = kwargs.get("topic", "AI and startups")
        context = kwargs.get("context", kwargs.get("summary", ""))
        plan = kwargs.get("plan", [])

        if plan and not kwargs.get("topic"):
            first = plan[0] if plan else {}
            topic = first.get("title", topic)
            context = first.get("summary", context)

        prompt = NEWSLETTER_PROMPT.format(brand=self.brand, topic=topic, context=context or "No additional context.")

        try:
            from ai_core.llm_router import generate
            draft = generate(prompt=prompt, temperature=0.65, max_tokens=1000)
        except Exception as exc:
            self.logger.warning("Newsletter generation failed: %s", exc)
            draft = f"[Newsletter generation failed for: {topic}]"

        # Extract subject line
        subject = ""
        for line in draft.splitlines():
            if line.upper().startswith("SUBJECT:"):
                subject = line.split(":", 1)[1].strip()
                break

        return {
            "drafts": [{
                "brand": self.brand,
                "topic": topic,
                "platform": "newsletter",
                "content_type": "newsletter_draft",
                "draft": draft,
                "subject_line": subject,
                "llm_generated": True,
                "word_count": len(draft.split()),
            }],
        }

    def format_output(self, data: Any) -> str:
        drafts = data.get("drafts", [])
        if not drafts:
            return "📧 No newsletters generated."
        d = drafts[0]
        lines = [
            f"\n📧 Newsletter — {d.get('topic', '')}",
            f"   Subject: {d.get('subject_line', 'N/A')}",
            "",
        ]
        for line in d.get("draft", "").splitlines():
            lines.append(f"  {line}")
        return "\n".join(lines)
