"""Instagram caption helper (stub)."""
from typing import Dict


def format_caption(text: str) -> str:
    return text.strip()[:2100]


def post_instagram(text: str, *, dry_run: bool = True) -> Dict:
    payload = {"platform": "instagram", "caption": format_caption(text)}
    payload["status"] = "dry_run" if dry_run else "queued"
    return payload
