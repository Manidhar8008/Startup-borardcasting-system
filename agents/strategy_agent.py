# -*- coding: utf-8 -*-
"""Strategy Agent — Determines content topics, platform strategy, and posting schedule.

Wraps the existing planner_agent logic and adds platform strategy and
growth experiment recommendations. Inherits from BaseAgent.
"""

from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from agents import planner_agent
from memory import topic_memory


@register
class StrategyAgent(BaseAgent):
    name = "strategy"
    role = "strategist"
    description = (
        "Determines content topics, platform strategy, posting schedules, "
        "and growth experiments based on research results and memory."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Build a scored content plan from research results.

        Expected kwargs:
            research_results (list): Topics from the research agent.
            morning_notes (dict, optional): Parsed founder notes.
            quantity (int): Number of tasks to generate (default 5).
            formats (list, optional): Preferred content formats.
            language (str): Target language.

        Returns:
            Dict with 'plan' (list of tasks) and 'strategy_insights'.
        """
        research_results = kwargs.get("research_results", [])
        morning_notes = kwargs.get("morning_notes")
        quantity = kwargs.get("quantity", 5)
        formats = kwargs.get("formats")
        language = kwargs.get("language", "")

        # Delegate to the existing planner_agent for LLM-powered planning
        plan = planner_agent.run(
            research_results,
            brand=self.brand,
            morning_notes=morning_notes,
            quantity=quantity,
            formats=formats,
            language=language,
        )

        # Add strategy insights from memory
        insights = self._build_strategy_insights()

        return {
            "plan": plan,
            "strategy_insights": insights,
        }

    def _build_strategy_insights(self) -> Dict[str, Any]:
        """Generate strategy insights from topic memory."""
        top = topic_memory.top_performers(self.brand, limit=3)
        recommended = topic_memory.recommended_topics(self.brand, limit=3)
        recent = topic_memory.recent_topics(self.brand, limit=3)

        return {
            "top_performing_topics": [t["topic"] for t in top],
            "recommended_fresh_topics": [t["topic"] for t in recommended],
            "recently_used": [t["topic"] for t in recent],
            "suggestion": (
                "Focus on recommended topics — they scored high but haven't been used recently."
                if recommended
                else "Build more publishing history to unlock strategy insights."
            ),
        }

    def format_output(self, data: Any) -> str:
        plan = data.get("plan", [])
        insights = data.get("strategy_insights", {})

        lines = [planner_agent.format_output(plan)]

        if insights.get("top_performing_topics"):
            lines.append("\n📊 Strategy Insights:")
            lines.append(f"  🏆 Top Performers: {', '.join(insights['top_performing_topics'])}")
            if insights.get("recommended_fresh_topics"):
                lines.append(f"  💡 Recommended Next: {', '.join(insights['recommended_fresh_topics'])}")
            lines.append(f"  📝 {insights.get('suggestion', '')}")

        return "\n".join(lines)
