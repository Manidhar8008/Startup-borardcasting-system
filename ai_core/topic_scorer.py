"""
ai_core/topic_scorer.py — Topic Intelligence: scores and ranks topics for content planning.

Scoring dimensions:
  trend_score        — keyword-based proxy for trending relevance
  recency_score      — bias toward topics not used recently (from memory)
  brand_alignment    — how well the topic matches brand keywords
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# ── Brand keyword maps for alignment scoring ───────────────────────────────────

_BRAND_KEYWORDS: Dict[str, List[str]] = {
    "janani_ai": [
        "founder", "philosophy", "vision", "behavior", "ai", "startup",
        "vernacular", "regional", "tier-2", "warangal", "india",
    ],
    "mw_ai_data_systems": [
        "data", "pipeline", "warehouse", "analytics", "mlops", "infra",
        "systems", "database", "etl", "real-time", "query",
    ],
    "mw_ai_news": [
        "news", "headline", "update", "policy", "funding", "research",
        "release", "launch", "regulation", "breakthrough",
    ],
    "mw_ai_edu": [
        "tutorial", "learn", "course", "student", "beginner", "how-to",
        "step-by-step", "guide", "python", "hands-on", "code",
    ],
}

# High-value trend signals (simple keyword heuristics)
_TREND_KEYWORDS = [
    "llm", "gpt", "agent", "automation", "fine-tuning", "rag",
    "prompt", "open-source", "local model", "ollama", "deepseek",
    "startup", "productivity", "cost", "india", "tier-2",
    "2025", "2026", "latest", "new", "breakthrough", "just released",
]


def _trend_score(text: str) -> float:
    """0.0–1.0 based on presence of trending keywords."""
    low = text.lower()
    hits = sum(1 for kw in _TREND_KEYWORDS if kw in low)
    return min(hits / max(len(_TREND_KEYWORDS) * 0.25, 1), 1.0)


def _brand_alignment_score(text: str, brand: str) -> float:
    """0.0–1.0 based on overlap with brand keyword vocabulary."""
    keywords = _BRAND_KEYWORDS.get(brand, [])
    if not keywords:
        return 0.5
    low = text.lower()
    hits = sum(1 for kw in keywords if kw in low)
    return min(hits / max(len(keywords) * 0.3, 1), 1.0)


def _recency_score(topic_title: str, memory_records: List[Dict]) -> float:
    """
    0.0–1.0 — higher = less recently used (fresh topic).
    Topics never used get 1.0. Topics used today get 0.1.
    """
    now = datetime.now(timezone.utc)
    title_low = topic_title.lower().strip()

    for rec in memory_records:
        if rec.get("topic", "").lower().strip() == title_low:
            last_used_str = rec.get("last_used", "")
            if not last_used_str:
                return 0.5
            try:
                last_used = datetime.fromisoformat(last_used_str.replace("Z", "+00:00"))
                days_ago = (now - last_used).total_seconds() / 86400
                # 1 day ago → 0.3, 7 days → 0.7, 30+ days → 1.0
                return min(0.3 + (days_ago / 30) * 0.7, 1.0)
            except Exception:
                return 0.5

    return 1.0  # Never used — maximum freshness


def score_topics(
    topics: List[Dict],
    focus_topics: Optional[List[str]] = None,
    brand: str = "janani_ai",
    memory_records: Optional[List[Dict]] = None,
) -> List[Dict]:
    """
    Score and sort a list of research topic dicts.

    Args:
        topics: List of dicts with at least 'title' and 'summary' keys.
        focus_topics: Founder's declared focus areas (from morning notes).
        brand: Active brand for alignment scoring.
        memory_records: Past topic usage records from topic_memory.

    Returns:
        Sorted list of topic dicts, each augmented with a 'score' dict and 'total_score'.
    """
    focus_topics   = focus_topics or []
    memory_records = memory_records or []
    focus_text     = " ".join(focus_topics).lower()

    scored = []
    for topic in topics:
        title   = topic.get("title", "")
        summary = topic.get("summary", "")
        text    = f"{title} {summary}"

        ts  = _trend_score(text)
        rs  = _recency_score(title, memory_records)
        bas = _brand_alignment_score(text, brand)

        # Founder focus boost: if topic aligns with today's focus, +0.2 bonus
        focus_boost = 0.2 if any(kw in text.lower() for kw in focus_text.split()) else 0.0

        # Weighted total
        total = round(
            (ts * 0.30) + (rs * 0.25) + (bas * 0.30) + (focus_boost * 0.15),
            4,
        )

        scored.append({
            **topic,
            "scores": {
                "trend":          round(ts, 3),
                "recency":        round(rs, 3),
                "brand_alignment": round(bas, 3),
                "focus_boost":    round(focus_boost, 3),
            },
            "total_score": total,
        })

    scored.sort(key=lambda x: x["total_score"], reverse=True)
    return scored


__all__ = ["score_topics"]
