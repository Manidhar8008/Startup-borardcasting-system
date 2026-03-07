"""Aggregate metrics per platform."""
from typing import Dict, List
from . import engagement_tracker


def totals_by_platform() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for event in engagement_tracker.events(limit=1000):
        platform = event.get("platform", "unknown")
        counts[platform] = counts.get(platform, 0) + 1
    return counts


def filter_by_brand(brand: str) -> List[Dict]:
    return [e for e in engagement_tracker.events(limit=1000) if e.get("brand") == brand]
