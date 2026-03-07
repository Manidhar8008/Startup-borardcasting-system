from datetime import datetime
from typing import Iterable, Optional, Sequence

from ai_core import content_optimizer
from . import prompt_engine


SECTION_ORDER = ["Hook", "Insight", "Example", "CTA"]


def generate_post(
    topic: str,
    brand: str,
    *,
    research_snippets: Optional[Iterable[str]] = None,
    kb_tags: Optional[Sequence[str]] = None,
    content_length: str = "short",
    platform: str | None = None,
) -> dict:
    """Create a structured draft with the required sections (Hook, Insight, Example, CTA)."""
    structure = prompt_engine.load_structure(brand)
    prompt = prompt_engine.generate_prompt(
        topic,
        brand,
        research_snippets=research_snippets,
        kb_tags=kb_tags,
        content_length=content_length,
        platform=platform,
    )

    voice = structure.get("voice", "concise")
    cta_style = structure.get("cta_style", "invite feedback")
    location_focus = "Tier-2 India (Warangal)"

    research_text = "; ".join(research_snippets or [])
    knowledge = prompt_engine.load_knowledge_base(brand, tags=kb_tags, limit=2)
    kb_line = "; ".join(k.get("summary", "") for k in knowledge)
    knowledge_example = knowledge[0].get("summary") if knowledge else ""

    hook = f"Why {topic} matters to {location_focus} right now."
    insight = f"{voice}: {research_text or kb_line or 'Share one sharp takeaway.'}"
    example = knowledge_example or "Small step: run a 48-hour experiment and measure lift."
    cta = cta_style

    sections = {
        "hook": hook,
        "insight": insight,
        "example": example,
        "cta": cta,
    }

    draft_lines = [
        f"Hook: {hook}",
        "",
        f"Insight: {insight}",
        "",
        f"Example: {example}",
        "",
        f"CTA: {cta}",
    ]

    draft_text = "\n".join(draft_lines)

    draft = {
        "brand": brand,
        "topic": topic,
        "content_length": content_length,
        "platform": platform,
        "sections": sections,
        "draft": draft_text,
        "prompt": prompt,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    return content_optimizer.optimize_draft(draft, structure)
