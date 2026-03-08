# -*- coding: utf-8 -*-
"""Blog publishing helper — outputs markdown files, optional CMS API."""
import os
from pathlib import Path
from typing import Dict

BLOG_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "blog"


def format_blog(text: str, *, title: str = "") -> Dict:
    return {
        "title": title or text.split("\n")[0][:80],
        "body": text.strip(),
        "word_count": len(text.split()),
    }


def publish_blog(text: str, *, title: str = "", dry_run: bool = True) -> Dict:
    formatted = format_blog(text, title=title)
    token = os.getenv("BLOG_API_KEY")

    if dry_run or not token:
        # Save as markdown file locally
        if not dry_run:
            BLOG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            slug = formatted["title"].lower().replace(" ", "-")[:40]
            path = BLOG_OUTPUT_DIR / f"{slug}.md"
            path.write_text(f"# {formatted['title']}\n\n{formatted['body']}", encoding="utf-8")
            return {"platform": "blog", "status": "saved", "path": str(path), **formatted}
        return {"platform": "blog", "status": "dry_run", **formatted}

    # Future: implement CMS API call
    return {"platform": "blog", "status": "queued", **formatted}
