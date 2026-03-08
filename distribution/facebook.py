# -*- coding: utf-8 -*-
"""Facebook publishing helper (stub with dry-run support)."""
import os
from typing import Dict


def format_post(text: str) -> str:
    return text.strip()[:5000]


def post_facebook(text: str, *, dry_run: bool = True) -> Dict:
    formatted = format_post(text)
    token = os.getenv("FACEBOOK_TOKEN")

    if dry_run or not token:
        return {"platform": "facebook", "status": "dry_run", "text": formatted}

    # Future: implement Graph API call
    return {"platform": "facebook", "status": "queued", "text": formatted}
