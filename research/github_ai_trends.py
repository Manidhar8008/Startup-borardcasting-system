"""Fetch trending AI repositories from GitHub trending HTML (no auth required)."""
import logging
import re
from typing import List, Dict
from urllib.request import urlopen, Request

logger = logging.getLogger("research")

TRENDING_URL = "https://github.com/trending/python?since=daily"

_SAMPLE = [
    {
        "title": "open-agent-kit",
        "name": "example/open-agent-kit",
        "url": "https://github.com/example/open-agent-kit",
        "description": "Starter kit for production-grade AI agents.",
        "summary": "Starter kit for production-grade AI agents.",
        "stars_today": 320,
        "source": "github_trending",
    },
    {
        "title": "vision-transformer-lite",
        "name": "example/vision-transformer-lite",
        "url": "https://github.com/example/vision-transformer-lite",
        "description": "Smaller ViT variant tuned for edge devices.",
        "summary": "Smaller ViT variant tuned for edge devices.",
        "stars_today": 180,
        "source": "github_trending",
    },
]


def _parse_trending(html: str) -> List[Dict]:
    items: List[Dict] = []
    repo_blocks = re.findall(r"<h2 class=\"lh-condensed\">(.*?)</p>", html, flags=re.S)
    for block in repo_blocks:
        name_match = re.search(r"href=\"(/[^\"]+)\"", block)
        desc_match = re.search(r"<p class=\"col-9.+?>(.*?)</p>", block, flags=re.S)
        stars_match = re.search(r"([0-9,]+) stars today", block)

        name = name_match.group(1).strip("/") if name_match else ""
        description = re.sub(r"\s+", " ", desc_match.group(1).strip()) if desc_match else ""
        stars = int(stars_match.group(1).replace(",", "")) if stars_match else 0

        if name:
            items.append(
                {
                    "title": name.split("/")[-1],
                    "name": name,
                    "url": f"https://github.com/{name}",
                    "description": description,
                    "summary": description,
                    "stars_today": stars,
                    "source": "github_trending",
                }
            )
    return items


def fetch_trending(*, limit: int = 5, offline: bool = False) -> List[Dict]:
    if offline:
        return _SAMPLE[:limit]

    try:
        req = Request(TRENDING_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=8) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        logger.info("github_trending_failed", extra={"error": str(exc)})
        return _SAMPLE[:limit]

    parsed = _parse_trending(html)
    return parsed[:limit] if parsed else _SAMPLE[:limit]


if __name__ == "__main__":
    for repo in fetch_trending(limit=2, offline=True):
        print(f"{repo['name']} ({repo['stars_today']}?)")
