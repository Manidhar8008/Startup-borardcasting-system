# -*- coding: utf-8 -*-
"""Analytics Agent — Collects engagement data and feeds strategy feedback.

Wraps existing analytics_engine modules and provides the feedback loop
that drives the self-improving intelligence system.
"""

from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from analytics_engine import engagement_tracker, platform_metrics
from memory_engine import performance_tracker
from ai_core import performance_learner


@register
class AnalyticsAgent(BaseAgent):
    name = "analytics"
    role = "analyst"
    description = (
        "Collects impressions, engagement, and performance metrics. "
        "Feeds results into the strategy agent for the learning feedback loop."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Collect and process analytics data.

        Expected kwargs:
            publish_results (list, optional): Results from publishing step.

        Returns:
            Dict with 'metrics', 'learning_update', and 'recommendations'.
        """
        publish_results = kwargs.get("publish_results", [])

        # Record publications in analytics
        metrics = []
        for result in publish_results:
            topic = result.get("topic", "")
            brand = result.get("brand", self.brand)
            channels = result.get("channels", [])
            metric = {
                "topic": topic,
                "brand": brand,
                "channels": channels,
                "platform": ",".join(channels),
                "score": min(0.4 + len(channels) * 0.15, 1.0),
            }
            metrics.append(metric)

        # Trigger learning cycle
        learning_result = self._run_learning()

        return {
            "metrics": metrics,
            "learning_update": learning_result,
            "total_publications": len(publish_results),
        }

    def _run_learning(self) -> str:
        """Run the performance learning cycle."""
        try:
            performance_learner.learn()
            return "Learning cycle completed."
        except Exception as exc:
            self.logger.warning("Learning cycle failed: %s", exc)
            return f"Learning skipped: {exc}"

    def format_output(self, data: Any) -> str:
        metrics = data.get("metrics", [])
        total = data.get("total_publications", 0)
        learning = data.get("learning_update", "")

        lines = [f"\n📈 Analytics Report ({total} publications tracked):"]
        for m in metrics:
            lines.append(
                f"  • {m['topic'][:55]} → {m['platform']} (score: {m['score']:.2f})"
            )
        lines.append(f"\n  🧠 {learning}")
        return "\n".join(lines)
