"""LinkedIn publishing with basic retry support."""
import os
import time
from typing import Dict

import requests

API_URL = "https://api.linkedin.com/v2/ugcPosts"
RETRIES = 3
BACKOFF = 1.5


def format_post(text: str) -> str:
    return text.strip()


def _post(payload: Dict, token: str) -> Dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    error = None
    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            if response.status_code < 300:
                return {"status": "sent", "response": response.json()}
            error = {"status": response.status_code, "body": response.text}
        except Exception as exc:
            error = {"status": "error", "body": str(exc)}
        time.sleep(BACKOFF * attempt)
    return {"status": "failed", "error": error}


def post_linkedin(text: str, *, dry_run: bool = True) -> Dict:
    formatted = format_post(text)
    token = os.getenv("LINKEDIN_ACCESS_TOKEN") or os.getenv("LINKEDIN_TOKEN")
    author = os.getenv("LINKEDIN_PAGE_ID", "urn:li:organization:0")

    if dry_run or not token:
        return {"platform": "linkedin", "status": "dry_run", "text": formatted}

    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": formatted},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    result = _post(payload, token)
    result.update({"platform": "linkedin", "text": formatted})
    return result
