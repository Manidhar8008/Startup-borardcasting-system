# -*- coding: utf-8 -*-
"""Trend Agent — Collects signals from multiple sources to detect trending topics.

Sources: RSS, YouTube, Reddit, Google News, Twitter/X trends.
Outputs ranked trend signals with velocity scores.
"""

import logging
import time
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register

logger = logging.getLogger("agent.trend")

TREND_ANALYSIS_PROMPT = """You are JAN, a trend intelligence analyst for brand '{brand}'.

Analyze these raw signals and extract the top trending topics.

For each topic, estimate:
- velocity: how fast it's growing (high/medium/low)
- relevance: how relevant to {brand}'s audience (high/medium/low)
- window: how long this trend will last (hours/days/weeks)

Raw signals:
\"\"\"
{signals}
\"\"\"

Output EXACTLY as a list:
TREND: <topic name>
VELOCITY: <high|medium|low>
RELEVANCE: <high|medium|low>
WINDOW: <hours|days|weeks>
SOURCE: <where detected>

---

List 5-8 trends. No preamble."""


def _velocity_score(v: str) -> float:
    return {"high": 1.0, "medium": 0.6, "low": 0.3}.get(v.lower(), 0.5)


def _relevance_score(r: str) -> float:
    return {"high": 1.0, "medium": 0.6, "low": 0.3}.get(r.lower(), 0.5)


def _parse_trends(raw: str) -> List[Dict]:
    """Parse LLM output into structured trend dicts."""
    trends = []
    current: Dict = {}

    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "---":
            if current.get("topic"):
                current["score"] = round(
                    _velocity_score(current.get("velocity", "medium")) * 0.5 +
                    _relevance_score(current.get("relevance", "medium")) * 0.5, 2
                )
                trends.append(current)
            current = {}
            continue

        upper = line.upper()
        if upper.startswith("TREND:"):
            current["topic"] = line.split(":", 1)[1].strip()
        elif upper.startswith("VELOCITY:"):
            current["velocity"] = line.split(":", 1)[1].strip().lower()
        elif upper.startswith("RELEVANCE:"):
            current["relevance"] = line.split(":", 1)[1].strip().lower()
        elif upper.startswith("WINDOW:"):
            current["window"] = line.split(":", 1)[1].strip().lower()
        elif upper.startswith("SOURCE:"):
            current["source"] = line.split(":", 1)[1].strip()

    # Don't forget last entry
    if current.get("topic"):
        current["score"] = round(
            _velocity_score(current.get("velocity", "medium")) * 0.5 +
            _relevance_score(current.get("relevance", "medium")) * 0.5, 2
        )
        trends.append(current)

    return sorted(trends, key=lambda t: t.get("score", 0), reverse=True)


@register
class TrendAgent(BaseAgent):
    name = "trend"
    role = "trend_intelligence"
    description = (
        "Collects signals from RSS, YouTube, Reddit, Google News, and Twitter/X "
        "to detect trending topics with velocity scores."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Collect trend signals from multiple sources.

        Expected kwargs:
            query (str): Seed query for trend detection.
            sources (list): Which sources to poll (default: all).

        Returns:
            Dict with 'trends' list and metadata.
        """
        query = kwargs.get("query", kwargs.get("topic", "AI and technology"))
        enabled = set(kwargs.get("sources", ["rss", "youtube", "brain"]))
        signals: List[str] = []
        source_counts: Dict[str, int] = {}

        # 1. RSS / Google News
        if "rss" in enabled:
            try:
                from research.research_pipeline import _fetch_rss
                items = _fetch_rss(query, limit=8)
                for item in items:
                    signals.append(f"[RSS] {item.get('title', '')} — {item.get('summary', '')[:100]}")
                source_counts["rss"] = len(items)
            except Exception:
                source_counts["rss"] = 0

        # 2. YouTube
        if "youtube" in enabled:
            try:
                from research.research_pipeline import _fetch_youtube
                items = _fetch_youtube(query, limit=5)
                for item in items:
                    signals.append(f"[YouTube] {item.get('title', '')} — {item.get('summary', '')[:100]}")
                source_counts["youtube"] = len(items)
            except Exception:
                source_counts["youtube"] = 0

        # 3. Brain input / founder notes
        if "brain" in enabled:
            try:
                from research.research_pipeline import _fetch_brain_input
                items = _fetch_brain_input(self.brand)
                for item in items:
                    signals.append(f"[Founder] {item.get('title', '')} — {item.get('summary', '')[:100]}")
                source_counts["brain"] = len(items)
            except Exception:
                source_counts["brain"] = 0

        # 4. Perplexity (live trends)
        if "perplexity" in enabled:
            try:
                from research.research_pipeline import _fetch_perplexity
                items = _fetch_perplexity(query, self.brand)
                for item in items:
                    signals.append(f"[Perplexity] {item.get('title', '')}")
                source_counts["perplexity"] = len(items)
            except Exception:
                source_counts["perplexity"] = 0

        if not signals:
            return {
                "trends": [],
                "source_counts": source_counts,
                "status": "no_signals",
            }

        # Use Gemini to analyze and rank trends
        combined = "\n".join(signals[:25])
        prompt = TREND_ANALYSIS_PROMPT.format(brand=self.brand, signals=combined)

        try:
            from ai_core.llm_router import generate
            raw = generate(prompt=prompt, temperature=0.4, max_tokens=1200)
            trends = _parse_trends(raw)
        except Exception as exc:
            self.logger.warning("Trend analysis failed: %s", exc)
            # Fallback: raw signals as trends
            trends = [
                {"topic": s.split("]", 1)[1].split("—")[0].strip(), "velocity": "medium",
                 "relevance": "medium", "score": 0.5, "source": s.split("]")[0].strip("[]}"), "window": "days"}
                for s in signals[:8]
            ]

        return {
            "trends": trends,
            "source_counts": source_counts,
            "total_signals": len(signals),
            "status": "analyzed",
        }

    def format_output(self, data: Any) -> str:
        trends = data.get("trends", [])
        counts = data.get("source_counts", {})
        if not trends:
            return "📊 No trends detected."

        lines = [
            f"\n📊 Trend Intelligence — {len(trends)} trends from {data.get('total_signals', 0)} signals",
            f"   Sources: {', '.join(f'{k}({v})' for k, v in counts.items() if v > 0)}",
        ]
        for i, t in enumerate(trends, 1):
            velocity_icon = {"high": "🔥", "medium": "📈", "low": "➡️"}.get(t.get("velocity", ""), "•")
            lines.append(
                f"\n  {i}. {velocity_icon} {t.get('topic', '')}"
                f"\n     Velocity: {t.get('velocity', '?')} | Relevance: {t.get('relevance', '?')} "
                f"| Window: {t.get('window', '?')} | Score: {t.get('score', 0):.2f}"
            )
        return "\n".join(lines)
