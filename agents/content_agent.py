# -*- coding: utf-8 -*-
"""Content Agent (v2) — LLM-powered Hook/Insight/Example/CTA draft generation.

Refactored to inherit from BaseAgent and register with the agent registry.
Uses prompt_loader for template management instead of hardcoded prompts.
"""

import logging
import re
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register

try:
    from ai_core.llm_router import generate as llm_generate
except ImportError:
    from ai_core.llm_brain import generate_text as llm_generate

logger = logging.getLogger("agent.content")

# Platform-specific writing tips
PLATFORM_TIPS = {
    "twitter":  "Write in a punchy, shareable tone. Use line breaks for clarity.",
    "linkedin": "Professional but human tone. Encourage comments at the end.",
    "youtube":  "Conversational and energetic. Works as a spoken script.",
}


def _build_content_prompt(task: Dict) -> str:
    """Build LLM prompt for content generation."""
    topic = task.get("title", "AI and startups")
    brand = task.get("brand", "janani_ai")
    platform = task.get("platform", "linkedin")
    content_type = task.get("content_type", "insight")
    content_length = task.get("content_length", "short")
    summary = task.get("summary", "")
    rationale = task.get("rationale", "")

    length_guide = (
        "Keep each section under 40 words. Total post under 150 words."
        if content_length == "short"
        else "Each section can be 60-100 words. Total post under 400 words."
    )

    # Try loading from prompt template, fall back to inline
    try:
        from prompts.prompt_loader import load_prompt
        return load_prompt(
            "content_prompts/social_post.md",
            brand=brand,
            platform=platform,
            content_type=content_type,
            topic=topic,
            context=summary or rationale or "No additional context.",
            length_guide=length_guide,
            platform_tips=PLATFORM_TIPS.get(platform, "Clear and engaging tone."),
        )
    except Exception:
        # Inline fallback
        return f"""You are JAN, content writer for brand '{brand}'.
Platform: {platform} ({PLATFORM_TIPS.get(platform, 'Clear and engaging tone.')})
Content type: {content_type}
Topic: {topic}
Context: {summary or rationale or 'No additional context.'}
{length_guide}

Write a social media post with EXACTLY these four labelled sections:
Hook: <attention-grabbing opening line or question>
Insight: <the core idea or data point>
Example: <concrete real-world example or story>
CTA: <clear call to action>

Output only the four sections. No preamble, no markdown formatting, no extra text.
"""


def _parse_llm_draft(raw: str, task: Dict) -> str:
    """Extract Hook/Insight/Example/CTA from LLM output."""
    sections = {}
    current = None
    buf: List[str] = []

    for line in raw.splitlines():
        m = re.match(r"^(Hook|Insight|Example|CTA)\s*:\s*(.*)", line, flags=re.IGNORECASE)
        if m:
            if current:
                sections[current] = " ".join(buf).strip()
            current = m.group(1).capitalize()
            buf = [m.group(2).strip()] if m.group(2).strip() else []
        elif current:
            buf.append(line.strip())

    if current:
        sections[current] = " ".join(buf).strip()

    if len(sections) >= 3:
        parts = []
        for label in ("Hook", "Insight", "Example", "CTA"):
            if label in sections:
                parts.append(f"{label}: {sections[label]}")
        return "\n\n".join(parts)

    return raw.strip()


@register
class ContentAgent(BaseAgent):
    name = "content"
    role = "content_creator"
    description = (
        "Generates platform-specific content: LinkedIn posts, Twitter threads, "
        "Instagram captions, reels scripts, YouTube short scripts, blog outlines."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Generate LLM-powered drafts from a content plan.

        Expected kwargs:
            plan (list): List of task dicts from the strategy agent.

        Returns:
            Dict with 'drafts' (list of draft dicts).
        """
        plan = kwargs.get("plan", [])
        if not plan:
            return {"drafts": [], "error": "No plan provided."}

        drafts = []
        for task in plan:
            prompt = _build_content_prompt(task)
            raw_text = llm_generate(prompt=prompt)
            draft_text = _parse_llm_draft(raw_text, task)

            # Platform-optimize via content transformer
            platform = task.get("platform", "linkedin")
            try:
                from network_engine.content_transformer import transform
                transformed = transform(draft_text, platform, brand=task.get("brand", self.brand))
                draft_text = transformed.get("text") or transformed.get("caption") or transformed.get("script") or transformed.get("body") or draft_text
            except Exception:
                pass  # Use raw draft if transformer fails

            draft = {
                "brand": task.get("brand", self.brand),
                "topic": task.get("title", ""),
                "content_type": task.get("content_type", "insight"),
                "content_length": task.get("content_length", "short"),
                "platform": task.get("platform"),
                "task_id": task.get("id"),
                "draft": draft_text,
                "llm_generated": True,
            }
            drafts.append(draft)
            logger.info("Content drafted for '%s' on %s", task.get("title"), task.get("platform"))

        return {"drafts": drafts}

    def format_output(self, data: Any) -> str:
        drafts = data.get("drafts", []) if isinstance(data, dict) else data
        marker = "🤖" if any(d.get("llm_generated") for d in drafts) else "✍️"
        lines = [f"\n{marker}  Generated {len(drafts)} Draft(s):"]
        for i, d in enumerate(drafts, 1):
            lines.append(f"\n  ─── Draft {i}: {d.get('topic', 'Untitled')} ───")
            lines.append(f"  Brand     : {d.get('brand')}")
            lines.append(f"  Platform  : {d.get('platform', 'N/A')}")
            lines.append(f"  Type      : {d.get('content_type', 'N/A')}")
            lines.append("")
            for line in d.get("draft", "").splitlines():
                lines.append(f"  {line}")
        return "\n".join(lines)


# ── Backward compatibility ────────────────────────────────────────────────────
# Keep module-level functions so existing imports (jan_manager, main.py) still work.

def run(tasks: List[Dict]) -> List[Dict]:
    """Legacy API: generate drafts from task list."""
    agent = ContentAgent()
    result = agent.run(plan=tasks)
    return result.get("drafts", [])


def format_output(drafts: List[Dict]) -> str:
    """Legacy API: format drafts for display."""
    agent = ContentAgent()
    return agent.format_output({"drafts": drafts})
