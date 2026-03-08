# -*- coding: utf-8 -*-
"""Memory Agent — Abstracts all memory operations for the intelligence system.

Provides a unified interface for topic memory queries, knowledge retrieval,
and context expansion. Future home for vector/semantic search.
"""

from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from memory import topic_memory


@register
class MemoryAgent(BaseAgent):
    name = "memory"
    role = "memory_keeper"
    description = (
        "Manages persistent intelligence: topic memory, knowledge retrieval, "
        "user preferences, and performance analytics."
    )
    tools = ["notebook_query", "source_get_content"]

    def run(self, **kwargs) -> Dict[str, Any]:
        """Query and manage memory.

        Expected kwargs:
            action (str): 'recall', 'store', 'insights' (default: 'insights')
            topic (str, optional): Topic to store or recall.
            performance_score (float, optional): Score for store action.

        Returns:
            Dict with memory data.
        """
        action = kwargs.get("action", "insights")

        if action == "store":
            return self._store(
                topic=kwargs.get("topic", ""),
                performance_score=kwargs.get("performance_score", 0.5),
            )
        elif action == "recall":
            return self._recall(topic=kwargs.get("topic", ""))
        else:
            return self._insights()

    def _store(self, topic: str, performance_score: float) -> Dict[str, Any]:
        """Store a topic usage record."""
        if not topic:
            return {"status": "error", "error": "No topic provided."}
        record = topic_memory.record_usage(topic, self.brand, performance_score=performance_score)
        return {"status": "stored", "record": record}

    def _recall(self, topic: str) -> Dict[str, Any]:
        """Recall memory records related to a topic."""
        all_recs = topic_memory.all_records(self.brand)
        if topic:
            key = topic.strip().lower()
            matches = [r for r in all_recs if key in r.get("topic", "").lower()]
        else:
            matches = all_recs
        return {"status": "success", "records": matches, "count": len(matches)}

    def _insights(self) -> Dict[str, Any]:
        """Generate memory insights summary."""
        return {
            "status": "success",
            "total_records": len(topic_memory.all_records(self.brand)),
            "top_performers": topic_memory.top_performers(self.brand, limit=5),
            "recent": topic_memory.recent_topics(self.brand, limit=5),
            "recommended": topic_memory.recommended_topics(self.brand, limit=5),
        }

    def format_output(self, data: Any) -> str:
        if data.get("status") == "stored":
            rec = data.get("record", {})
            return f"💾 Stored: '{rec.get('topic', '')}' (score: {rec.get('performance_score', 0):.2f})"

        if "records" in data:
            recs = data["records"]
            lines = [f"🧠 Memory Recall ({data.get('count', 0)} records):"]
            for r in recs[:10]:
                lines.append(f"  • {r['topic'][:50]} | used: {r.get('times_used', 0)}x | score: {r.get('performance_score', 0):.2f}")
            return "\n".join(lines)

        # Insights
        lines = [f"🧠 Memory Insights ({data.get('total_records', 0)} total records):"]
        for label, key in [("🏆 Top", "top_performers"), ("🕐 Recent", "recent"), ("💡 Recommended", "recommended")]:
            items = data.get(key, [])
            if items:
                lines.append(f"\n  {label}:")
                for r in items:
                    lines.append(f"    • {r['topic'][:50]}")
        return "\n".join(lines)
