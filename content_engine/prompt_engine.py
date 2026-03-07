import json
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
DATABASES_DIR = ROOT / "databases"
KNOWLEDGE_BASE_DIR = ROOT / "knowledge_base"

KB_MAP = {
    "janani_ai": "janani_ai_kb.json",
    "mw_ai_data_systems": "mw_ai_data_kb.json",
    "mw_ai_news": "mw_ai_news_kb.json",
    "mw_ai_edu": "mw_ai_edu_kb.json",
}


def _safe_load_json(path: Path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_structure(brand: str) -> dict:
    """Load brand structure (voice, sections, tools) from databases/<brand>/structure.json."""
    path = DATABASES_DIR / brand / "structure.json"
    data = _safe_load_json(path)
    if not data:
        # Provide a sensible fallback to avoid crashing when onboarding a new brand.
        data = {
            "brand": brand,
            "voice": "concise, pragmatic",
            "audience": "general tech audience",
            "brief_sections": ["Hook", "Insight", "Example", "CTA"],
            "tools": [],
            "cta_style": "invite feedback",
            "content_ratio": {"long": 0.5, "short": 0.5},
            "tone": ["neutral"],
        }
    return data


def load_knowledge_base(brand: str, *, limit: int = 3, tags: Optional[Sequence[str]] = None) -> List[dict]:
    """Fetch a few knowledge base entries for the brand to ground prompts.

    Args:
        brand: brand key matching the databases folder.
        limit: max number of snippets to include.
        tags: optional tag filter.
    """
    kb_file = KB_MAP.get(brand, f"{brand}_kb.json")
    kb_path = KNOWLEDGE_BASE_DIR / kb_file
    entries = _safe_load_json(kb_path) or []

    if tags:
        tag_set = {t.lower() for t in tags}
        entries = [e for e in entries if tag_set.intersection({t.lower() for t in e.get("tags", [])})]

    return entries[:limit]


def _format_snippets(snippets: Iterable[dict]) -> str:
    lines = []
    for item in snippets:
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source", "")
        date = item.get("date", "")
        lines.append(f"- {title} ({source}, {date}): {summary}")
    return "\n".join(lines) if lines else "- None yet"


def generate_prompt(
    topic: str,
    brand: str,
    *,
    research_snippets: Optional[Iterable[str]] = None,
    kb_tags: Optional[Sequence[str]] = None,
    content_length: str = "short",
    platform: str | None = None,
    location_focus: str = "Tier-2 India (Warangal)",
) -> str:
    """Create a structured prompt for content generation."""
    structure = load_structure(brand)
    knowledge = load_knowledge_base(brand, tags=kb_tags)

    sections = "; ".join(structure.get("brief_sections", []))
    tools = ", ".join(structure.get("tools", []))
    voice = structure.get("voice", "concise")
    audience = structure.get("audience", "general tech audience")
    cta_style = structure.get("cta_style", "invite feedback")
    tone = ", ".join(structure.get("tone", []))

    research_block = "\n".join(research_snippets or []) if research_snippets else "(none provided)"
    kb_block = _format_snippets(knowledge)

    prompt = f"""
You are the content engine for brand '{brand}'.
Audience: {audience}
Tone: {tone}
Voice: {voice}
CTA style: {cta_style}
Location focus: {location_focus}
Content length: {content_length}
Platform: {platform or 'not specified'}

Topic: {topic}

Brand structure sections: {sections}
Preferred tools: {tools}

Grounding facts from knowledge base:
{kb_block}

Recent research snippets:
{research_block}

Compose a social media insight post that follows the sections in order (Hook, Insight, Example, CTA).
Keep it under 120 words for short content or under 400 words for long content.
"""

    return prompt.strip()
