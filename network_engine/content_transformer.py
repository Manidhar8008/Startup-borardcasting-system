"""Transform long-form content into platform-specific formats."""
from textwrap import wrap
from typing import Dict


def _sanitize(text: str) -> str:
    return text.strip().replace("\n", " ")


def generate_linkedin_post(content: str, *, brand: str) -> Dict:
    text = _sanitize(content)
    bullets = wrap(text, width=180)[:3]
    body = "\n- ".join([bullets[0]] + bullets[1:]) if bullets else text[:220]
    return {
        "platform": "linkedin",
        "brand": brand,
        "text": f"{body}\n\n#AI #{brand}"
    }


def generate_twitter_thread(content: str, *, brand: str) -> Dict:
    text = _sanitize(content)
    chunks = wrap(text, width=240)
    thread = [f"{idx+1}/ {chunk}" for idx, chunk in enumerate(chunks[:5])]
    return {"platform": "twitter", "brand": brand, "thread": thread}


def generate_instagram_caption(content: str, *, brand: str) -> Dict:
    text = _sanitize(content)
    caption = f"{text[:180]}...\n\nMore in stories. #{brand}"
    return {"platform": "instagram", "brand": brand, "caption": caption}


def generate_youtube_script(content: str, *, brand: str) -> Dict:
    text = _sanitize(content)
    intro = f"Welcome back! Today we explore: {text[:100]}..."
    body = text[:1200]
    outro = "Subscribe for Tier-2 to Tier-1 AI playbooks."
    return {
        "platform": "youtube",
        "brand": brand,
        "script": "\n\n".join(["INTRO:", intro, "BODY:", body, "OUTRO:", outro]),
    }
