"""JAN Publisher Agent: simulates publishing drafts (dry-run) and records topic usage."""

import logging
from datetime import datetime
from typing import Dict, List

from distribution import publisher_router
from memory import topic_memory

logger = logging.getLogger("publishing")


def run(drafts: List[Dict], *, dry_run: bool = True) -> List[Dict]:
    """
    Simulate publishing each draft to its target channels.
    Records topic usage in memory after each publish.

    Returns:
        List of publish result dicts.
    """
    results   = []
    timestamp = datetime.utcnow().isoformat() + "Z"

    for draft in drafts:
        content_type = draft.get("content_type", "insight")
        channels     = publisher_router.route(content_type)
        topic        = draft.get("topic", "Untitled")
        brand        = draft.get("brand", "janani_ai")

        result = {
            "topic":        topic,
            "brand":        brand,
            "content_type": content_type,
            "channels":     channels,
            "status":       "simulated" if dry_run else "published",
            "published_at": timestamp,
            "dry_run":      dry_run,
        }
        results.append(result)

        # Step 5: Record topic usage in memory
        # Assign a base performance score derived from channel count (proxy metric)
        perf_score = min(0.4 + len(channels) * 0.15, 1.0)
        topic_memory.record_usage(topic, brand, performance_score=perf_score)
        logger.info("Recorded usage for topic '%s' (brand=%s, score=%.2f)", topic, brand, perf_score)

    return results


def format_output(results: List[Dict]) -> str:
    mode  = "🔵 DRY-RUN" if results and results[0].get("dry_run") else "🚀 LIVE"
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
