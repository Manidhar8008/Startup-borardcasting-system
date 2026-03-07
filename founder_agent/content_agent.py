"""Agent that turns approved ideas into drafts."""
from typing import Iterable

from content_engine import generator
from media_engine import image_generator
from decision_engine import approval_queue, topic_selector


def draft_from_approved(brand: str):
    queue = approval_queue.ApprovalQueue(brand)
    approved = queue.list_approved()
    created = []
    for idx, idea in enumerate(approved):
        content_length = idea.get("content_length") or topic_selector.pick_content_length(brand, idx)
        draft = generator.generate_post(
            idea.get("title", ""),
            brand,
            research_snippets=[idea.get("summary", "")],
            content_length=content_length,
        )
        draft["idea_id"] = idea["id"]
        draft["content_type"] = idea.get("content_type")
        draft["image"] = image_generator.generate_placeholder(idea.get("title", ""), dry_run=True)
        queue.add_draft(draft)
        queue.set_idea_status(idea["id"], "drafted")
        created.append(draft)
    return created
