"""Surface viral topics based on engagement score."""
from typing import Dict, List
from . import engagement_tracker


def update_with_metric(topic: str, metrics: Dict):
    score = metrics.get("score") or metrics.get("engagement", 0)
    engagement_tracker.record(topic, metrics | {"score": score})


def top_topics(limit: int = 5) -> List[Dict]:
    events = engagement_tracker.events(limit=1000)
    ranked = sorted(events, key=lambda e: e.get("score", 0), reverse=True)
    return ranked[:limit]
