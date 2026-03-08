# -*- coding: utf-8 -*-
"""Performance Learner — Analyzes engagement data and learns patterns.

Reads topic memory + engagement events, computes topic × platform matrices,
identifies high-performing patterns, and writes to learned_patterns.json.
"""

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from analytics_engine import engagement_tracker, platform_metrics

logger = logging.getLogger("engine")

PATTERNS_FILE = Path(__file__).resolve().parent.parent / "memory_engine" / "learned_patterns.json"


def _load_topic_memory() -> List[Dict]:
    """Load topic memory records."""
    try:
        from memory import topic_memory
        return topic_memory.all_records()
    except Exception:
        return []


def _compute_topic_boosts(events: List[Dict], memory: List[Dict]) -> Dict[str, float]:
    """Compute which topic keywords correlate with high engagement."""
    keyword_scores: Dict[str, List[float]] = defaultdict(list)

    for event in events:
        topic = event.get("topic", "")
        score = (
            event.get("likes", 0) * 2
            + event.get("comments", 0) * 3
            + event.get("shares", 0) * 4
            + event.get("clicks", 0) * 1
            + event.get("impressions", 0) * 0.01
        )
        # Extract keywords from topic
        for word in topic.lower().split():
            if len(word) > 3:
                keyword_scores[word].append(score)

    # Add memory performance scores
    for rec in memory:
        topic = rec.get("topic", "")
        perf = rec.get("performance_score", 0.5)
        for word in topic.lower().split():
            if len(word) > 3:
                keyword_scores[word].append(perf * 100)

    # Average scores per keyword, normalize to 0-1
    boosts = {}
    if keyword_scores:
        max_avg = max(
            (sum(scores) / len(scores)) for scores in keyword_scores.values()
        ) or 1.0
        for keyword, scores in keyword_scores.items():
            avg = sum(scores) / len(scores)
            boosts[keyword] = round(avg / max_avg, 4)

    return dict(sorted(boosts.items(), key=lambda x: x[1], reverse=True)[:50])


def _compute_platform_preferences(events: List[Dict]) -> Dict[str, float]:
    """Determine which platforms have the best engagement rates."""
    platform_engagement: Dict[str, List[float]] = defaultdict(list)

    for event in events:
        platform = event.get("platform", "unknown")
        engagement = (
            event.get("likes", 0)
            + event.get("comments", 0) * 2
            + event.get("shares", 0) * 3
        )
        platform_engagement[platform].append(engagement)

    prefs = {}
    for platform, scores in platform_engagement.items():
        prefs[platform] = round(sum(scores) / max(len(scores), 1), 2)

    return prefs


def _compute_content_type_wins(events: List[Dict]) -> Dict[str, float]:
    """Determine which content types perform best."""
    type_scores: Dict[str, List[float]] = defaultdict(list)

    for event in events:
        ct = event.get("content_type", "unknown")
        score = event.get("score", 0) + event.get("likes", 0) + event.get("shares", 0)
        type_scores[ct].append(score)

    wins = {}
    for ct, scores in type_scores.items():
        wins[ct] = round(sum(scores) / max(len(scores), 1), 2)

    return wins


def learn() -> Dict:
    """Run the full learning cycle.

    1. Read engagement events + topic memory
    2. Compute topic boosts, platform prefs, content type wins
    3. Write patterns to learned_patterns.json
    4. Return learning summary

    Returns:
        Dict with pattern counts for each dimension.
    """
    events = engagement_tracker.events(limit=1000)
    memory = _load_topic_memory()
    platform_totals = platform_metrics.totals_by_platform()

    topic_boosts = _compute_topic_boosts(events, memory)
    platform_prefs = _compute_platform_preferences(events)
    content_type_wins = _compute_content_type_wins(events)

    result = {
        "topic_boosts": topic_boosts,
        "platform_preferences": platform_prefs,
        "content_type_wins": content_type_wins,
        "platform_totals": platform_totals,
        "events_analyzed": len(events),
        "memory_records": len(memory),
    }

    # Persist
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PATTERNS_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info(
        "Learning complete: %d topic boosts, %d platform prefs, %d content wins from %d events",
        len(topic_boosts), len(platform_prefs), len(content_type_wins), len(events),
    )

    return result


__all__ = ["learn"]
