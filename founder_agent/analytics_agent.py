"""Agent that records engagement back into analytics engine."""
from analytics_engine import engagement_tracker, viral_topics


def record_publication(topic: str, metrics: dict):
    engagement_tracker.record(topic, metrics)
    viral_topics.update_with_metric(topic, metrics)
