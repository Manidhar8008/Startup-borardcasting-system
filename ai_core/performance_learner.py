# -*- coding: utf-8 -*-
"""Performance Learner v2 — Extended learning engine.

Tracks: likes, comments, shares, follower growth, CTR.
Updates: topic scoring weights, content templates, posting schedules.
Writes: learned_patterns.json + learned_schedules.json
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from analytics_engine import engagement_tracker, platform_metrics

logger = logging.getLogger("engine")

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory_engine"
PATTERNS_FILE = MEMORY_DIR / "learned_patterns.json"
SCHEDULES_FILE = MEMORY_DIR / "learned_schedules.json"
TEMPLATES_FILE = MEMORY_DIR / "learned_templates.json"


def _load_topic_memory() -> List[Dict]:
    try:
        from memory import topic_memory
        return topic_memory.all_records()
    except Exception:
        return []


def _compute_topic_boosts(events: List[Dict], memory: List[Dict]) -> Dict[str, float]:
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
        for word in topic.lower().split():
            if len(word) > 3:
                keyword_scores[word].append(score)
    for rec in memory:
        topic = rec.get("topic", "")
        perf = rec.get("performance_score", 0.5)
        for word in topic.lower().split():
            if len(word) > 3:
                keyword_scores[word].append(perf * 100)
    boosts = {}
    if keyword_scores:
        max_avg = max((sum(s) / len(s)) for s in keyword_scores.values()) or 1.0
        for kw, scores in keyword_scores.items():
            avg = sum(scores) / len(scores)
            boosts[kw] = round(avg / max_avg, 4)
    return dict(sorted(boosts.items(), key=lambda x: x[1], reverse=True)[:50])


def _compute_platform_preferences(events: List[Dict]) -> Dict[str, float]:
    platform_engagement: Dict[str, List[float]] = defaultdict(list)
    for event in events:
        platform = event.get("platform", "unknown")
        engagement = (
            event.get("likes", 0)
            + event.get("comments", 0) * 2
            + event.get("shares", 0) * 3
        )
        platform_engagement[platform].append(engagement)
    return {p: round(sum(s) / max(len(s), 1), 2) for p, s in platform_engagement.items()}


def _compute_content_type_wins(events: List[Dict]) -> Dict[str, float]:
    type_scores: Dict[str, List[float]] = defaultdict(list)
    for event in events:
        ct = event.get("content_type", "unknown")
        score = event.get("score", 0) + event.get("likes", 0) + event.get("shares", 0)
        type_scores[ct].append(score)
    return {ct: round(sum(s) / max(len(s), 1), 2) for ct, s in type_scores.items()}


# ── New v2: Schedule Learning ──────────────────────────────────────────────────

def _learn_posting_schedules(events: List[Dict]) -> Dict[str, Dict]:
    """Learn optimal posting times per platform from engagement data."""
    platform_hours: Dict[str, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))

    for event in events:
        platform = event.get("platform", "unknown")
        ts = event.get("timestamp", event.get("published", ""))
        engagement = event.get("likes", 0) + event.get("comments", 0) * 2

        hour = None
        if isinstance(ts, str) and len(ts) >= 13:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                hour = dt.hour
            except (ValueError, TypeError):
                pass

        if hour is not None:
            platform_hours[platform][hour].append(engagement)

    schedules: Dict[str, Dict] = {}
    for platform, hours_data in platform_hours.items():
        if not hours_data:
            continue
        # Find top 3 hours by avg engagement
        hour_avgs = {
            h: sum(scores) / len(scores)
            for h, scores in hours_data.items()
        }
        best_hours = sorted(hour_avgs, key=hour_avgs.get, reverse=True)[:3]
        schedules[platform] = {
            "best_hours_utc": best_hours,
            "best_hour_label": [f"{h:02d}:00" for h in best_hours],
            "avg_engagement": {h: round(hour_avgs[h], 1) for h in best_hours},
        }

    return schedules


def _learn_content_templates(events: List[Dict]) -> Dict[str, Dict]:
    """Learn which content structures perform best per platform."""
    platform_templates: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for event in events:
        platform = event.get("platform", "unknown")
        template = event.get("template", event.get("content_type", "default"))
        score = event.get("likes", 0) + event.get("shares", 0) * 2 + event.get("comments", 0)
        platform_templates[platform][template].append(score)

    templates: Dict[str, Dict] = {}
    for platform, tmpl_data in platform_templates.items():
        best = max(tmpl_data, key=lambda t: sum(tmpl_data[t]) / len(tmpl_data[t]), default="default")
        templates[platform] = {
            "best_template": best,
            "template_scores": {
                t: round(sum(s) / len(s), 2) for t, s in tmpl_data.items()
            },
        }
    return templates


# ── New v2: Extended Metrics Tracking ──────────────────────────────────────────

def _compute_growth_metrics(events: List[Dict]) -> Dict:
    """Track follower growth and CTR trends."""
    followers = {}
    ctr_data: Dict[str, List[float]] = defaultdict(list)

    for event in events:
        platform = event.get("platform", "unknown")
        if "followers" in event:
            followers[platform] = event["followers"]
        if "impressions" in event and event["impressions"] > 0 and "clicks" in event:
            ctr = event["clicks"] / event["impressions"]
            ctr_data[platform].append(ctr)

    return {
        "follower_snapshot": followers,
        "avg_ctr_by_platform": {
            p: round(sum(rates) / len(rates), 4) for p, rates in ctr_data.items()
        },
    }


def learn() -> Dict:
    """Run the full learning cycle.

    1. Read engagement events + topic memory
    2. Compute topic boosts, platform prefs, content type wins
    3. Learn optimal posting schedules
    4. Learn best content templates
    5. Track growth metrics (followers, CTR)
    6. Write all patterns to disk
    """
    events = engagement_tracker.events(limit=1000)
    memory = _load_topic_memory()
    platform_totals = platform_metrics.totals_by_platform()

    topic_boosts = _compute_topic_boosts(events, memory)
    platform_prefs = _compute_platform_preferences(events)
    content_type_wins = _compute_content_type_wins(events)
    schedules = _learn_posting_schedules(events)
    templates = _learn_content_templates(events)
    growth = _compute_growth_metrics(events)

    result = {
        "topic_boosts": topic_boosts,
        "platform_preferences": platform_prefs,
        "content_type_wins": content_type_wins,
        "platform_totals": platform_totals,
        "schedules": schedules,
        "templates": templates,
        "growth": growth,
        "events_analyzed": len(events),
        "memory_records": len(memory),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    # Persist all files
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    PATTERNS_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if schedules:
        SCHEDULES_FILE.write_text(json.dumps(schedules, indent=2), encoding="utf-8")
    if templates:
        TEMPLATES_FILE.write_text(json.dumps(templates, indent=2), encoding="utf-8")

    logger.info(
        "Learning v2: %d boosts, %d platform prefs, %d type wins, %d schedules from %d events",
        len(topic_boosts), len(platform_prefs), len(content_type_wins), len(schedules), len(events),
    )

    return result


def get_learned_schedules() -> Dict:
    """Load learned posting schedules."""
    if SCHEDULES_FILE.exists():
        return json.loads(SCHEDULES_FILE.read_text(encoding="utf-8"))
    return {}


def get_learned_patterns() -> Dict:
    """Load all learned patterns."""
    if PATTERNS_FILE.exists():
        return json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
    return {}


__all__ = ["learn", "get_learned_schedules", "get_learned_patterns"]
