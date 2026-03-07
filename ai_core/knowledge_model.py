"""Build a lightweight knowledge snapshot from KB, brain inputs, and analytics."""
import json
from pathlib import Path

from analytics_engine import engagement_tracker
from brain_input import brain_parser

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "knowledge_base"
MEMORY_PATH = ROOT / "memory_engine" / "topic_memory.json"
DB_DIR = ROOT / "databases"


def _load_kb() -> list:
    entries = []
    for kb_file in KB_DIR.glob("*.json"):
        try:
            data = json.loads(kb_file.read_text(encoding="utf-8"))
            entries.extend(data if isinstance(data, list) else [])
        except Exception:
            continue
    return entries


def _load_databases() -> list:
    records = []
    for brand_dir in DB_DIR.iterdir():
        if not brand_dir.is_dir():
            continue
        for fname in ["ideas.json", "drafts.json", "published.json"]:
            path = brand_dir / fname
            if path.exists():
                try:
                    records.extend(json.loads(path.read_text(encoding="utf-8")))
                except Exception:
                    continue
    return records


def build_snapshot() -> dict:
    snapshot = {
        "knowledge": _load_kb(),
        "founder_inputs": brain_parser.parse_all_inputs(),
        "analytics": engagement_tracker.events(limit=200),
        "history": _load_databases(),
    }
    MEMORY_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


__all__ = ["build_snapshot"]
