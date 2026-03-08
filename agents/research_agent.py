# -*- coding: utf-8 -*-
"""Research Agent (v2) — Gathers topics using existing infrastructure.

Refactored to inherit from BaseAgent and register with the agent registry.
Delegates core logic to founder_agent.research_agent for backward compatibility.
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from founder_agent import research_agent as _core_research


@register
class ResearchAgent(BaseAgent):
    name = "research"
    role = "researcher"
    description = (
        "Analyzes PDFs, research notes, bookmarks, YouTube transcripts, and articles. "
        "Extracts ideas, insights, trends, and hooks."
    )
    tools = ["notebook_query", "research_start", "source_get_content"]

    def run(self, **kwargs) -> Dict[str, Any]:
        """Gather research topics.

        Expected kwargs:
            topic (str): Research topic query (default: '').

        Returns:
            Dict with 'research_results' (list of topic dicts).
        """
        topic = kwargs.get("topic", "")
        results = _core_research.gather(self.brand, topic=topic, offline=True)
        return {"research_results": results}

    def format_output(self, data: Any) -> str:
        results = data.get("research_results", []) if isinstance(data, dict) else data
        lines = [f"\n🔍 Research Results ({len(results)} found):"]
        for i, r in enumerate(results, 1):
            lines.append(f"  {i}. {r.get('title', 'Untitled')}")
            lines.append(f"     {r.get('summary', '')}")
        return "\n".join(lines)
