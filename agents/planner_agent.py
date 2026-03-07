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


# ── LLM prompt builder ────────────────────────────────────────────────────────

def _build_plan_prompt(
    ranked_topics: List[Dict],
    brand: str,
    morning_notes: Optional[Dict] = None,
) -> str:
    # Top 6 scored topics for the LLM — include score info for context
    topics_block = "\n".join(
        f"  - [{t.get('total_score', 0):.2f}] {t.get('title', '')}: {t.get('summary', '')}"
        for t in ranked_topics[:6]
    )

    notes_block = ""
    if morning_notes:
        focus = ", ".join(morning_notes.get("focus_topics", []))
        goals = "\n".join(f"  - {g}" for g in morning_notes.get("content_goals", []))
        notes_block = (
            f"\nFounder's focus for today: {focus}\n"
            f"Content goals:\n{goals}\n"
        )

    return f"""You are JAN, a personal AI content manager for the brand '{brand}'.
{notes_block}
Based on the ranked research topics (format: [score] title: summary) and the founder's daily goals,
create a focused content plan for today. Prefer higher-scored topics.

Ranked topics:
{topics_block}

Return a JSON array of up to 5 content tasks. Each task must have these exact keys:
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


def _fallback_plan(ranked_topics: List[Dict], brand: str) -> List[Dict]:
    """Static fallback when LLM output cannot be parsed."""
    now   = datetime.utcnow().strftime("%Y-%m-%d")
    tasks = []
    for i, t in enumerate(ranked_topics[:5]):
        tasks.append({
            "id":             f"task-{i+1}",
            "title":          t.get("title", "Untitled"),
            "summary":        t.get("summary", ""),
            "brand":          brand,
            "content_type":   CONTENT_TYPES[i % len(CONTENT_TYPES)],
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
) -> List[Dict]:
    """
    Rank topics with Topic Intelligence, then build an LLM-powered content plan.

    Steps:
      1. Load topic memory records for recency scoring
      2. Score and rank all research topics via topic_scorer
      3. Build LLM prompt with ranked topics + morning notes
      4. Parse LLM output → task list
      5. Fallback to static plan if LLM output unparseable
    """
    if not research_results:
        return []

    # Step 1: Load memory
    memory_records = topic_memory.all_records(brand)

    # Step 2: Score topics
    focus_topics   = (morning_notes or {}).get("focus_topics", [])
    ranked_topics  = topic_scorer.score_topics(
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
    prompt = _build_plan_prompt(ranked_topics, brand, morning_notes)
    raw    = llm_brain.generate_text(prompt)
    tasks  = _parse_llm_plan(raw, brand)

    if not tasks:
        tasks = _fallback_plan(ranked_topics, brand)

    logger.info("Planner created %d tasks for brand '%s'", len(tasks), brand)
    return tasks


def format_output(tasks: List[Dict]) -> str:
    marker = "🤖" if any(t.get("llm_generated") for t in tasks) else "📋"
    lines  = [f"\n{marker} Today's Content Plan ({len(tasks)} tasks):"]
    for t in tasks:
        lines.append(f"\n  [{t['id']}] {t['title']}")
        lines.append(
            f"        Platform : {t['platform']} | "
            f"Type: {t['content_type']} | Length: {t['content_length']}"
        )
        if t.get("rationale"):
            lines.append(f"        Why      : {t['rationale']}")
    return "\n".join(lines)
