# -*- coding: utf-8 -*-
"""JAN Planner Agent: LLM-powered planning with Topic Intelligence scoring."""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from ai_core import llm_brain, topic_scorer
from memory import topic_memory

logger = logging.getLogger("engine")

CONTENT_TYPES = ["thread", "insight", "short_explainer", "tutorial", "case_study"]
PLATFORMS     = ["twitter", "linkedin", "youtube"]

# Map workflow format names → planner content_type names
_FORMAT_TO_CONTENT_TYPE: Dict[str, str] = {
    "thread":          "thread",
    "insight":         "insight",
    "short_video":     "short_explainer",
    "tutorial":        "tutorial",
    "long_form":       "case_study",
    "case_study":      "case_study",
    "short_explainer": "short_explainer",
}


# ── LLM prompt builder ────────────────────────────────────────────────────────

def _build_plan_prompt(
    ranked_topics: List[Dict],
    brand: str,
    morning_notes: Optional[Dict] = None,
    quantity: int = 5,
    formats: Optional[List[str]] = None,
    language: str = "",
) -> str:
    # Top topics for LLM context — include score
    topics_block = "\n".join(
        f"  - [{t.get('total_score', 0):.2f}] {t.get('title', '')}: {t.get('summary', '')}"
        for t in ranked_topics[:max(quantity, 6)]
    )

    notes_block = ""
    if morning_notes:
        focus = ", ".join(morning_notes.get("focus_topics", []))
        goals = "\n".join(f"  - {g}" for g in morning_notes.get("content_goals", []))
        notes_block = (
            f"\nFounder's focus for today: {focus}\n"
            f"Content goals:\n{goals}\n"
        )

    # Build content-type preference line
    preferred_types = ""
    if formats:
        type_names = [
            _FORMAT_TO_CONTENT_TYPE.get(f, f) for f in formats
        ]
        preferred_types = (
            f"\nPreferred content types (in order): {', '.join(type_names)}. "
            "Use these types for the tasks where possible.\n"
        )

    # Language instruction
    lang_instruction = ""
    if language:
        lang_instruction = (
            f"\nIMPORTANT: All content should be planned for the '{language}' language audience.\n"
        )

    return f"""You are JAN, a personal AI content manager for the brand '{brand}'.
{notes_block}{preferred_types}{lang_instruction}
Based on the ranked research topics (format: [score] title: summary) and the founder's daily goals,
create a focused content plan. Prefer higher-scored topics.

Ranked topics:
{topics_block}

Return a JSON array of EXACTLY {quantity} content tasks. Each task must have these exact keys:
- "title": string — specific post title
- "summary": string — one sentence brief
- "content_type": one of ["thread", "insight", "short_explainer", "tutorial", "case_study"]
- "platform": one of ["twitter", "linkedin", "youtube"]
- "content_length": one of ["short", "long"]
- "rationale": string — one sentence explaining why this topic matters today

Output ONLY valid JSON. No markdown, no explanation, just the array.
"""


def _parse_llm_plan(raw: str, brand: str) -> List[Dict]:
    """Parse LLM JSON output into task dicts."""
    clean = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
    # Find first JSON array in the response
    arr_match = re.search(r"\[.*\]", clean, re.DOTALL)
    if arr_match:
        clean = arr_match.group(0)
    try:
        items = json.loads(clean)
        if not isinstance(items, list):
            raise ValueError("Expected a JSON array")
        now   = datetime.utcnow().strftime("%Y-%m-%d")
        tasks = []
        for i, item in enumerate(items):
            tasks.append({
                "id":             f"task-{i+1}",
                "title":          item.get("title", f"Topic {i+1}"),
                "summary":        item.get("summary", ""),
                "brand":          brand,
                "content_type":   item.get("content_type", CONTENT_TYPES[i % len(CONTENT_TYPES)]),
                "platform":       item.get("platform", PLATFORMS[i % len(PLATFORMS)]),
                "content_length": item.get("content_length", "short"),
                "rationale":      item.get("rationale", ""),
                "scheduled_for":  now,
                "llm_generated":  True,
            })
        return tasks
    except Exception as exc:
        logger.warning("Could not parse LLM plan JSON (%s). Falling back.", exc)
        return []


def _fallback_plan(
    ranked_topics: List[Dict],
    brand: str,
    quantity: int = 5,
    formats: Optional[List[str]] = None,
) -> List[Dict]:
    """Static fallback when LLM output cannot be parsed.

    Replicates topics if there are fewer research results than the requested
    quantity so the user always gets exactly `quantity` tasks.
    """
    now    = datetime.utcnow().strftime("%Y-%m-%d")
    tasks  = []
    # Cycle through topics to fill requested quantity
    topics_cycle = ranked_topics if ranked_topics else [{"title": "General AI Trends", "summary": "AI trends today.", "total_score": 0.5}]

    for i in range(quantity):
        t      = topics_cycle[i % len(topics_cycle)]
        # Pick content_type: prefer formats list, then fall back to cycling CONTENT_TYPES
        if formats:
            ct = _FORMAT_TO_CONTENT_TYPE.get(formats[i % len(formats)], CONTENT_TYPES[i % len(CONTENT_TYPES)])
        else:
            ct = CONTENT_TYPES[i % len(CONTENT_TYPES)]

        tasks.append({
            "id":             f"task-{i+1}",
            "title":          t.get("title", "Untitled"),
            "summary":        t.get("summary", ""),
            "brand":          brand,
            "content_type":   ct,
            "platform":       PLATFORMS[i % len(PLATFORMS)],
            "content_length": "short" if i % 2 == 0 else "long",
            "rationale":      f"Scored {t.get('total_score', 0):.2f} by Topic Intelligence",
            "scheduled_for":  now,
            "llm_generated":  False,
        })
    return tasks


# ── Public API ────────────────────────────────────────────────────────────────

def run(
    research_results: List[Dict],
    brand: str = "janani_ai",
    morning_notes: Optional[Dict] = None,
    quantity: int = 5,
    formats: Optional[List[str]] = None,
    language: str = "",
) -> List[Dict]:
    """
    Rank topics with Topic Intelligence, then build an LLM-powered content plan.

    Args:
        research_results : Topics gathered by research_agent.
        brand            : Active brand.
        morning_notes    : Parsed founder notes (focus_topics, content_goals).
        quantity         : How many tasks to produce (from workflow intent).
        formats          : Preferred content formats (from workflow intent).
        language         : Target language for the content (e.g. "telugu").

    Steps:
      1. Load topic memory records for recency scoring
      2. Score and rank all research topics via topic_scorer
      3. Build LLM prompt with ranked topics + quantity + formats + language
      4. Parse LLM output → task list of exactly `quantity` items
      5. Fallback to static plan (same size) if LLM output unparseable
    """
    if not research_results:
        return []

    quantity = max(1, min(quantity, 10))

    # Step 1: Load memory
    memory_records = topic_memory.all_records(brand)

    # Step 2: Score topics
    focus_topics  = (morning_notes or {}).get("focus_topics", [])
    ranked_topics = topic_scorer.score_topics(
        research_results,
        focus_topics=focus_topics,
        brand=brand,
        memory_records=memory_records,
    )
    logger.info(
        "Topic Intelligence: top topic='%s' (%.2f)",
        ranked_topics[0].get("title", "") if ranked_topics else "",
        ranked_topics[0].get("total_score", 0) if ranked_topics else 0,
    )

    # Step 3–5: LLM plan
    prompt = _build_plan_prompt(
        ranked_topics, brand, morning_notes,
        quantity=quantity, formats=formats, language=language,
    )
    raw   = llm_brain.generate_text(prompt)
    tasks = _parse_llm_plan(raw, brand)

    if not tasks:
        tasks = _fallback_plan(ranked_topics, brand, quantity=quantity, formats=formats)

    # Ensure we always return exactly quantity tasks
    if len(tasks) < quantity:
        extra = _fallback_plan(ranked_topics, brand, quantity=quantity - len(tasks), formats=formats)
        # Re-number
        for i, t in enumerate(extra, start=len(tasks)):
            t["id"] = f"task-{i+1}"
        tasks.extend(extra)
    tasks = tasks[:quantity]

    logger.info("Planner created %d tasks for brand '%s'", len(tasks), brand)
    return tasks


def format_output(tasks: List[Dict]) -> str:
    marker = "\U0001f916" if any(t.get("llm_generated") for t in tasks) else "\U0001f4cb"
    lines  = [f"\n{marker} Content Plan ({len(tasks)} task{'s' if len(tasks) != 1 else ''}):"]
    for t in tasks:
        lines.append(f"\n  [{t['id']}] {t['title']}")
        lines.append(
            f"        Platform : {t['platform']} | "
            f"Type: {t['content_type']} | Length: {t['content_length']}"
        )
        if t.get("rationale"):
            lines.append(f"        Why      : {t['rationale']}")
    return "\n".join(lines)
