"""Learn performance patterns from analytics data."""
import json
from pathlib import Path
from typing import Dict

from analytics_engine import engagement_tracker, platform_metrics

STORE = Path(__file__).resolve().parent.parent / "memory_engine" / "performance_tracker.json"


def learn() -> Dict:
    events = engagement_tracker.events(limit=500)
    platform_totals = platform_metrics.totals_by_platform()
    topic_scores: Dict[str, float] = {}
    for event in events:
        topic = event.get("topic") or event.get("title") or "unknown"
        score = float(event.get("score", 1))
        topic_scores[topic] = topic_scores.get(topic, 0) + score
    result = {
        "platform_totals": platform_totals,
        "topic_scores": topic_scores,
    }
    STORE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


__all__ = ["learn"]
