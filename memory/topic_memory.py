"""
memory/topic_memory.py — Persistent topic usage tracker for the Topic Intelligence Engine.

Stores per-topic records in memory/topic_memory.json:
  topic             — topic title (primary key, normalised lowercase)
  times_used        — how many times this topic was included in a published plan
  last_used         — ISO timestamp of last use
  performance_score — rolling average score (0.0–1.0, updated after publish)
  brand             — brand the topic belongs to
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("engine")

MEMORY_DIR  = Path(__file__).resolve().parent
MEMORY_FILE = MEMORY_DIR / "topic_memory.json"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> List[Dict]:
    if not MEMORY_FILE.exists():
        return []
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(records: List[Dict]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _key(topic: str) -> str:
    return topic.strip().lower()


# ── Public API ────────────────────────────────────────────────────────────────

def record_usage(topic: str, brand: str, *, performance_score: float = 0.5) -> Dict:
    """
    Record that a topic was used (published).

    Updates times_used, last_used, and rolling performance_score.
    Returns the updated record.
    """
    records   = _load()
    now_iso   = datetime.now(timezone.utc).isoformat()
    topic_key = _key(topic)

    for rec in records:
        if _key(rec.get("topic", "")) == topic_key:
            rec["times_used"] += 1
            rec["last_used"]   = now_iso
            # Rolling average: blend new score with history
            old_score = rec.get("performance_score", 0.5)
            rec["performance_score"] = round(
                old_score * 0.7 + performance_score * 0.3, 4
            )
            _save(records)
            logger.info("Updated topic memory for '%s'", topic)
            return rec

    # New topic — create record
    new_rec = {
        "topic":             topic,
        "brand":             brand,
        "times_used":        1,
        "last_used":         now_iso,
        "performance_score": round(performance_score, 4),
        "first_seen":        now_iso,
    }
    records.append(new_rec)
    _save(records)
    logger.info("Added new topic memory for '%s'", topic)
    return new_rec


def all_records(brand: Optional[str] = None) -> List[Dict]:
    """Return all memory records, optionally filtered by brand."""
    records = _load()
    if brand:
        records = [r for r in records if r.get("brand") == brand]
    return records


def top_performers(brand: Optional[str] = None, limit: int = 5) -> List[Dict]:
    """Return topics sorted by performance_score descending."""
    records = all_records(brand)
    return sorted(records, key=lambda r: r.get("performance_score", 0), reverse=True)[:limit]


def recent_topics(brand: Optional[str] = None, limit: int = 5) -> List[Dict]:
    """Return the most recently used topics."""
    records = all_records(brand)
    return sorted(records, key=lambda r: r.get("last_used", ""), reverse=True)[:limit]


def recommended_topics(brand: Optional[str] = None, limit: int = 5) -> List[Dict]:
    """
    Recommend topics that are high-performing but haven't been used recently.
    Score = performance_score / recency_penalty.
    Topics used very recently are deprioritised.
    """
    records = all_records(brand)
    now     = datetime.now(timezone.utc)

    def _reco_score(rec: Dict) -> float:
        perf      = rec.get("performance_score", 0.5)
        last_str  = rec.get("last_used", "")
        try:
            last = datetime.fromisoformat(last_str.replace("Z", "+00:00"))
            days = max((now - last).total_seconds() / 86400, 0.01)
        except Exception:
            days = 30.0
        # Topics used 7+ days ago surface more
        recency_factor = min(days / 7, 2.0)
        return perf * recency_factor

    return sorted(records, key=_reco_score, reverse=True)[:limit]


__all__ = [
    "record_usage",
    "all_records",
    "top_performers",
    "recent_topics",
    "recommended_topics",
]
