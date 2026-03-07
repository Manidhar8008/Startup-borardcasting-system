"""Auto-post flow: move drafts through approval and into distribution channels."""
from typing import Dict, Iterable, List

from decision_engine.approval_queue import ApprovalQueue
from distribution import twitter, linkedin, instagram, youtube

CHANNEL_MAP = {
    "twitter": twitter.post_tweet,
    "linkedin": linkedin.post_linkedin,
    "instagram": instagram.post_instagram,
    "youtube": youtube.schedule_upload,
}


def dispatch_to_channels(text: str, channels: Iterable[str], *, dry_run: bool = True) -> List[Dict]:
    results: List[Dict] = []
    for ch in channels:
        handler = CHANNEL_MAP.get(ch)
        if handler:
            if ch == "youtube":
                results.append(handler(title=text[:60], description=text, dry_run=dry_run))
            else:
                results.append(handler(text, dry_run=dry_run))
    return results


def autopost_drafts(brand: str, *, channels: Iterable[str], dry_run: bool = True) -> List[Dict]:
    queue = ApprovalQueue(brand)
    drafts = queue.list_drafts()
    posted: List[Dict] = []

    for draft in drafts:
        text = draft.get("draft") or draft.get("text") or ""
        channel_results = dispatch_to_channels(text, channels, dry_run=dry_run)
        queue.publish(draft["id"])
        posted.append({
            "draft_id": draft["id"],
            "topic": draft.get("topic", ""),
            "channels": channel_results,
        })

    return posted


if __name__ == "__main__":
    results = autopost_drafts("janani_ai", channels=["twitter", "linkedin"], dry_run=True)
    print(results)
