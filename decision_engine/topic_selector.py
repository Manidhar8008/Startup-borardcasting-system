"""Select and rank topics from research inputs."""
from typing import List, Dict, Iterable

from analytics_engine import viral_topics
from content_engine import prompt_engine


BRAND_KEYWORDS = {
    "mw_ai_data_systems": {"data", "lakehouse", "warehouse", "governance", "pipeline", "infra"},
    "mw_ai_news": {"policy", "funding", "launch", "model", "warangal", "hyderabad"},
    "mw_ai_edu": {"classroom", "student", "teacher", "edtech", "curriculum", "campus"},
    "janani_ai": {"founder", "experiment", "workflow", "agent", "philosophy", "future"},
}

AI_KEYWORDS = {"ai", "ml", "model", "agent", "llm", "inference"}
STARTUP_KEYWORDS = {"startup", "founder", "pmf", "revenue", "pricing", "go-to-market", "gtm"}
TIER2_KEYWORDS = {"warangal", "tier-2", "telangana", "hyderabad", "india"}

CONTENT_RATIO = {
    "mw_ai_data_systems": {"long": 0.6, "short": 0.4},
    "mw_ai_edu": {"long": 0.6, "short": 0.4},
    "janani_ai": {"long": 0.3, "short": 0.7},
    "mw_ai_news": {"long": 0.3, "short": 0.7},
}


def _contains_any(text: str, keywords) -> bool:
    return any(k in text for k in keywords)


def _kb_alignment(text: str, brand: str) -> float:
    kb_entries = prompt_engine.load_knowledge_base(brand, limit=5)
    tags = {t.lower() for entry in kb_entries for t in entry.get("tags", [])}
    return 1.0 if tags and _contains_any(text, tags) else 0.0


def _score_item(item: Dict, brand: str) -> float:
    summary = (item.get("summary") or item.get("description") or "").lower()
    title = (item.get("title") or "").lower()
    text = f"{title} {summary}"
    score = 0.0

    if _contains_any(text, AI_KEYWORDS):
        score += 2.0
    if _contains_any(text, STARTUP_KEYWORDS):
        score += 1.5
    if _contains_any(text, TIER2_KEYWORDS):
        score += 1.5

    for kw in BRAND_KEYWORDS.get(brand, set()):
        if kw in text:
            score += 1.0

    score += _kb_alignment(text, brand)
    viral_titles = {t.get("topic", "").lower() for t in viral_topics.top_topics(limit=20)}
    if title in viral_titles:
        score += 2.0

    if item.get("suggested_score"):
        score += float(item["suggested_score"])

    if len(summary) > 80:
        score += 0.5
    if item.get("stars_today"):
        score += min(item["stars_today"] / 200, 2)
    return score


def rank_topics(research_items: Iterable[Dict], brand: str, *, limit: int = 5) -> List[Dict]:
    ranked = sorted(research_items, key=lambda x: _score_item(x, brand), reverse=True)
    return ranked[:limit]


def pick_top_titles(research_items: Iterable[Dict], brand: str, *, limit: int = 3) -> List[str]:
    return [item.get("title", "") for item in rank_topics(research_items, brand, limit=limit)]


def pick_content_length(brand: str, index: int) -> str:
    """Assign content length according to brand ratios."""
    ratio = CONTENT_RATIO.get(brand, {"long": 0.5, "short": 0.5})
    cutoff = int(ratio["long"] * 10)
    return "long" if index < cutoff else "short"
