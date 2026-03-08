# -*- coding: utf-8 -*-
"""Newsletter publishing helper — generates email-ready content, optional Mailchimp/Resend API."""
import os
from typing import Dict


def format_newsletter(text: str, *, subject: str = "") -> Dict:
    lines = text.strip().split("\n")
    return {
        "subject_line": subject or lines[0][:80] if lines else "This week in AI",
        "preview_text": lines[0][:120] if lines else "",
        "body": text.strip(),
        "word_count": len(text.split()),
    }


def send_newsletter(text: str, *, subject: str = "", dry_run: bool = True) -> Dict:
    formatted = format_newsletter(text, subject=subject)
    token = os.getenv("NEWSLETTER_API_KEY")

    if dry_run or not token:
        return {"platform": "newsletter", "status": "dry_run", **formatted}

    # Future: implement Mailchimp/Resend API
    return {"platform": "newsletter", "status": "queued", **formatted}
