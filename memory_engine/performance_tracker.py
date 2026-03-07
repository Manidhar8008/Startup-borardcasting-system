"""Track engagement and surface viral topics."""
import json
from pathlib import Path
from typing import Dict, List

MEMORY_PATH = Path(__file__).resolve().parent / "topic_memory.json"


def _load_memory() -> Dict:
    if not MEMORY_PATH.exists():
        return {"topics": []}
    return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))


def _save_memory(data: Dict):
    MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_engagement(topic: str, metrics: Dict):
    data = _load_memory()
    data.setdefault("topics", [])
    data["topics"].append({"topic": topic, **metrics})
    _save_memory(data)


def top_topics(*, limit: int = 5) -> List[Dict]:
    data = _load_memory().get("topics", [])
    scored = sorted(data, key=lambda t: t.get("score", 0), reverse=True)
    return scored[:limit]
