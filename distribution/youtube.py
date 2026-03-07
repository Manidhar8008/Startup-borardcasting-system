"""YouTube publish helper (stub)."""
from typing import Dict


def format_metadata(title: str, description: str) -> Dict:
    return {
        "title": title[:90],
        "description": description[:4800],
    }


def schedule_upload(title: str, description: str, *, dry_run: bool = True) -> Dict:
    payload = {"platform": "youtube", **format_metadata(title, description)}
    payload["status"] = "dry_run" if dry_run else "queued"
    return payload
