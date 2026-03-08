# -*- coding: utf-8 -*-
"""Publisher Agent (v2) — Publishes drafts and records topic usage.

Refactored to inherit from BaseAgent and register with the agent registry.
Delegates core logic to existing distribution/publisher_router.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from distribution import publisher_router
from memory import topic_memory

logger = logging.getLogger("agent.publisher")


@register
class PublisherAgent(BaseAgent):
    name = "publisher"
    role = "publisher"
    description = (
        "Formats content, posts to platforms, and schedules publishing. "
        "Records topic usage in memory after each publish."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Publish drafts to target channels.

        Expected kwargs:
            drafts (list): Draft dicts from the content agent.
            dry_run (bool): Simulate publishing (default: True).

        Returns:
            Dict with 'publish_results' (list of result dicts).
        """
        drafts = kwargs.get("drafts", [])
        dry_run = kwargs.get("dry_run", True)

        if not drafts:
            return {"publish_results": [], "error": "No drafts to publish."}

        results = []
        timestamp = datetime.utcnow().isoformat() + "Z"

        for draft in drafts:
            content_type = draft.get("content_type", "insight")
            channels = publisher_router.route(content_type)
            topic = draft.get("topic", "Untitled")
            brand = draft.get("brand", self.brand)

            result = {
                "topic": topic,
                "brand": brand,
                "content_type": content_type,
                "channels": channels,
                "status": "simulated" if dry_run else "published",
                "published_at": timestamp,
                "dry_run": dry_run,
            }
            results.append(result)

            # Record topic usage in memory
            perf_score = min(0.4 + len(channels) * 0.15, 1.0)
            topic_memory.record_usage(topic, brand, performance_score=perf_score)
            logger.info("Published '%s' (brand=%s, score=%.2f)", topic, brand, perf_score)

        return {"publish_results": results}

    def format_output(self, data: Any) -> str:
        results = data.get("publish_results", []) if isinstance(data, dict) else data
        if not results:
            return "📤 No publications."
        mode = "🔵 DRY-RUN" if results[0].get("dry_run") else "🚀 LIVE"
        lines = [f"\n📤 Publishing Results [{mode}] — {len(results)} item(s):"]
        for r in results:
            channels_str = ", ".join(r.get("channels", []))
            lines.append(
                f"  ✅ {r['topic'][:60]}"
                f"\n     → Channels : {channels_str}"
                f"\n     → Status   : {r['status']}"
                f"\n     → Brand    : {r['brand']}"
            )
        return "\n".join(lines)


# ── Backward compatibility ────────────────────────────────────────────────────

def run(drafts: List[Dict], *, dry_run: bool = True) -> List[Dict]:
    """Legacy API: publish drafts."""
    agent = PublisherAgent()
    result = agent.run(drafts=drafts, dry_run=dry_run)
    return result.get("publish_results", [])


def format_output(results: List[Dict]) -> str:
    """Legacy API: format publish results."""
    agent = PublisherAgent()
    return agent.format_output({"publish_results": results})
