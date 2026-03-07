"""Persist engagement events across platforms."""
import json
from pathlib import Path
from typing import Dict, List

STORE = Path(__file__).resolve().parent / "engagement.json"


def _load() -> Dict:
    if not STORE.exists():
        return {"events": []}
    return json.loads(STORE.read_text(encoding="utf-8"))


def _save(data: Dict):
    STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record(topic: str, metrics: Dict):
    data = _load()
    data.setdefault("events", []).append({"topic": topic, **metrics})
    _save(data)


def events(limit: int = 100) -> List[Dict]:
    return _load().get("events", [])[-limit:]
