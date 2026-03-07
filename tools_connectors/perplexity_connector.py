"""Perplexity connector stub.

The real API requires an auth token; this helper keeps the interface consistent and
returns a deterministic placeholder when no token is provided.
"""
import json
import logging
import os
from typing import Dict, Optional
from urllib.request import Request, urlopen

logger = logging.getLogger("research")

API_URL = "https://api.perplexity.ai/chat/completions"


def ask_perplexity(prompt: str, *, api_key: Optional[str] = None) -> Dict:
    key = api_key or os.getenv("PERPLEXITY_API_KEY")
    if not key:
        return {
            "model": "perplexity-stub",
            "prompt": prompt,
            "answer": "Perplexity API key missing; returning placeholder summary.",
        }

    payload = {
        "model": "sonar-small-online",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
    }
    try:
        req = Request(API_URL, data=json.dumps(payload).encode("utf-8"))
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {key}")
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"model": payload["model"], "prompt": prompt, "answer": answer}
    except Exception as exc:
        logger.info("perplexity_call_failed", extra={"error": str(exc)})
        return {
            "model": "perplexity-stub",
            "prompt": prompt,
            "answer": "Perplexity call failed; placeholder used.",
        }
