"""Agent that routes drafts to platforms."""
import logging
from distribution import publisher_router
from automation import autopost
from decision_engine import approval_queue


def publish_ready(brand: str, *, dry_run: bool = True):
    queue = approval_queue.ApprovalQueue(brand)
    drafts = queue.list_drafts()
    results = []
    for draft in drafts:
        content_type = draft.get("content_type") or "insight"
        channels = publisher_router.route(content_type)
        result = autopost.dispatch_to_channels(draft.get("draft", ""), channels, dry_run=dry_run)
        queue.publish(draft["id"])
        results.append({"draft": draft["id"], "channels": channels, "result": result})
    logging.getLogger("publishing").info("distribution", extra={"brand": brand, "count": len(results), "dry_run": dry_run})
    return results
