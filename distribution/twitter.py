"""Twitter/X publishing with basic retry support."""
import os
import time
from textwrap import shorten
from typing import Dict

import requests

API_URL = "https://api.twitter.com/2/tweets"
RETRIES = 3
BACKOFF = 1.5


def format_tweet(text: str) -> str:
    return shorten(text.replace("\n", " "), width=270, placeholder="…")


def _post(payload: Dict, token: str) -> Dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
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


def post_tweet(text: str, *, dry_run: bool = True) -> Dict:
    formatted = format_tweet(text)
    token = os.getenv("TWITTER_API_KEY")

    if dry_run or not token:
        return {"platform": "twitter", "status": "dry_run", "text": formatted}

    payload = {"text": formatted}
    result = _post(payload, token)
    result.update({"platform": "twitter", "text": formatted})
    return result
