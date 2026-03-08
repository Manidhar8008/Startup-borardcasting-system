# -*- coding: utf-8 -*-
"""Persist and aggregate engagement events across platforms.

Upgraded with normalized metrics, per-topic and per-platform aggregation.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

STORE = Path(__file__).resolve().parent / "engagement.json"


def _load() -> Dict:
    if not STORE.exists():
        return {"events": []}
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except Exception:
        return {"events": []}


def _save(data: Dict):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record(topic: str, metrics: Dict):
    """Record an engagement event with normalized metrics.

    Expected metrics keys: impressions, likes, comments, shares, clicks,
    platform, brand, content_type.
    """
    data = _load()
    event = {
        "topic": topic,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "impressions": metrics.get("impressions", 0),
        "likes": metrics.get("likes", 0),
        "comments": metrics.get("comments", 0),
        "shares": metrics.get("shares", 0),
        "clicks": metrics.get("clicks", 0),
        "followers": metrics.get("followers", 0),
        "platform": metrics.get("platform", "unknown"),
        "brand": metrics.get("brand", ""),
        "content_type": metrics.get("content_type", ""),
        "score": metrics.get("score", 0),
    }
    data.setdefault("events", []).append(event)
    _save(data)


def events(limit: int = 100) -> List[Dict]:
    """Return most recent events."""
    return _load().get("events", [])[-limit:]


def summarize_by_topic(limit: int = 20) -> Dict[str, Dict]:
    """Aggregate engagement metrics per topic."""
    all_events = _load().get("events", [])
    topics: Dict[str, Dict] = {}

    for e in all_events:
        topic = e.get("topic", "unknown")
        if topic not in topics:
            topics[topic] = {"impressions": 0, "likes": 0, "comments": 0, "shares": 0, "clicks": 0, "count": 0}
        t = topics[topic]
        t["impressions"] += e.get("impressions", 0)
        t["likes"] += e.get("likes", 0)
        t["comments"] += e.get("comments", 0)
        t["shares"] += e.get("shares", 0)
        t["clicks"] += e.get("clicks", 0)
        t["count"] += 1

    # Sort by total engagement
    sorted_topics = dict(
        sorted(topics.items(), key=lambda x: sum(x[1].get(k, 0) for k in ("likes", "comments", "shares")), reverse=True)[:limit]
    )
    return sorted_topics


def summarize_by_platform() -> Dict[str, Dict]:
    """Aggregate engagement metrics per platform."""
    all_events = _load().get("events", [])
    platforms: Dict[str, Dict] = {}

    for e in all_events:
        platform = e.get("platform", "unknown")
        if platform not in platforms:
            platforms[platform] = {"impressions": 0, "likes": 0, "comments": 0, "shares": 0, "count": 0}
        p = platforms[platform]
        p["impressions"] += e.get("impressions", 0)
        p["likes"] += e.get("likes", 0)
        p["comments"] += e.get("comments", 0)
        p["shares"] += e.get("shares", 0)
        p["count"] += 1

    return platforms
