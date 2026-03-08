# -*- coding: utf-8 -*-
"""Topic Ranker Agent — Scores and ranks topics for content creation.

Scoring dimensions:
  1. Trend velocity (from TrendAgent)
  2. Audience relevance (brand alignment)
  3. Founder interest alignment (from brain input)
  4. Historical engagement (from memory)
  5. Recency penalty (avoid overused topics)
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register

# Weights for each scoring dimension
WEIGHTS = {
    "trend_velocity": 0.25,
    "audience_relevance": 0.20,
    "founder_interest": 0.20,
    "historical_engagement": 0.20,
    "recency_bonus": 0.15,
}


def _score_trend_velocity(topic: Dict) -> float:
    """Score based on trend velocity if available."""
    v = topic.get("velocity", "medium")
    return {"high": 1.0, "medium": 0.6, "low": 0.3}.get(str(v).lower(), 0.5)


def _score_audience_relevance(topic: Dict, brand: str) -> float:
    """Score based on brand keyword alignment."""
    brand_keywords = {
        "janani_ai": ["AI", "startup", "founder", "tech", "agent", "LLM", "automation", "creator"],
    }
    keywords = brand_keywords.get(brand, brand_keywords["janani_ai"])
    title = topic.get("topic", topic.get("title", "")).lower()
    summary = topic.get("summary", "").lower()
    text = f"{title} {summary}"
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return min(hits / max(len(keywords) * 0.3, 1), 1.0)


def _score_founder_interest(topic: Dict) -> float:
    """Score based on whether topic came from founder's brain input."""
    source = topic.get("source", "")
    if "brain" in source or "founder" in source or "morning" in source:
        return 1.0
    return 0.4


def _score_historical_engagement(topic: Dict, brand: str) -> float:
    """Score based on past topic performance from memory."""
    try:
        from memory import topic_memory
        records = topic_memory.all_records(brand)
        title = topic.get("topic", topic.get("title", "")).lower()
        for rec in records:
            if rec.get("topic", "").lower()[:30] == title[:30]:
                return min(rec.get("performance_score", 0.5), 1.0)
    except Exception:
        pass
    return 0.5  # neutral for new topics


def _score_recency(topic: Dict, brand: str) -> float:
    """Bonus for fresh topics, penalty for recently used ones."""
    try:
        from memory import topic_memory
        recent = topic_memory.recent_topics(brand, limit=10)
        title = topic.get("topic", topic.get("title", "")).lower()
        for rec in recent:
            if rec.get("topic", "").lower()[:30] == title[:30]:
                return 0.2  # Recently used — low bonus
        return 0.9  # Fresh topic — high bonus
    except Exception:
        return 0.6


def rank_topics(topics: List[Dict], brand: str = "janani_ai") -> List[Dict]:
    """Score and rank a list of topics.

    Args:
        topics: List of topic dicts (from TrendAgent or research).
        brand: Brand context for relevance scoring.

    Returns:
        Sorted list with 'rank_score' and dimension scores added.
    """
    scored = []
    for topic in topics:
        scores = {
            "trend_velocity": _score_trend_velocity(topic),
            "audience_relevance": _score_audience_relevance(topic, brand),
            "founder_interest": _score_founder_interest(topic),
            "historical_engagement": _score_historical_engagement(topic, brand),
            "recency_bonus": _score_recency(topic, brand),
        }
        rank_score = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
        topic_scored = {**topic, "dimension_scores": scores, "rank_score": round(rank_score, 3)}
        scored.append(topic_scored)

    return sorted(scored, key=lambda t: t["rank_score"], reverse=True)


@register
class TopicRanker(BaseAgent):
    name = "topic_ranker"
    role = "topic_intelligence"
    description = (
        "Ranks topics using 5 scoring dimensions: trend velocity, audience "
        "relevance, founder interest, historical engagement, and recency."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Rank topics for content planning.

        Expected kwargs:
            trends (list): Trend dicts from TrendAgent.
            topics (list): Raw topic dicts from research.

        Returns:
            Dict with 'ranked_topics' list.
        """
        # Accept from either TrendAgent or research pipeline
        topics = kwargs.get("trends", kwargs.get("topics", kwargs.get("research_results", [])))
        if not topics:
            return {"ranked_topics": [], "error": "No topics to rank."}

        ranked = rank_topics(topics, brand=self.brand)

        return {
            "ranked_topics": ranked,
            "top_topic": ranked[0] if ranked else {},
            "total_ranked": len(ranked),
        }

    def format_output(self, data: Any) -> str:
        ranked = data.get("ranked_topics", [])
        if not ranked:
            return "🏆 No topics ranked."

        lines = [f"\n🏆 Topic Rankings — {len(ranked)} topics scored"]
        for i, t in enumerate(ranked[:10], 1):
            scores = t.get("dimension_scores", {})
            topic_name = t.get("topic", t.get("title", "?"))
            lines.append(
                f"\n  {i}. {topic_name[:60]}"
                f"\n     Score: {t.get('rank_score', 0):.3f} | "
                f"Trend: {scores.get('trend_velocity', 0):.1f} "
                f"Audience: {scores.get('audience_relevance', 0):.1f} "
                f"Founder: {scores.get('founder_interest', 0):.1f} "
                f"History: {scores.get('historical_engagement', 0):.1f} "
                f"Fresh: {scores.get('recency_bonus', 0):.1f}"
            )
        return "\n".join(lines)
