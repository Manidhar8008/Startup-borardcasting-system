"""AI news scraper with Google News RSS fallback and location focus."""
import logging
import xml.etree.ElementTree as _et
from typing import List, Dict
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

logger = logging.getLogger("research")


def _build_feed(query: str, region: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-{region}&gl={region}&ceid={region}:en"


_FALLBACK_ITEMS = [
    {
        "title": "AI infra costs push teams to efficiency",
        "url": "https://example.com/ai-infra-efficiency",
        "published": "2026-02-28",
        "summary": "Teams tune batching and quantization to cut spend while keeping latency steady.",
        "source": "fallback",
    },
    {
        "title": "Policy momentum for synthetic media labels",
        "url": "https://example.com/policy-labels",
        "published": "2026-03-01",
        "summary": "Lawmakers advance disclosure rules that affect consumer apps and marketing.",
        "source": "fallback",
    },
]


def _parse_rss(xml_bytes: bytes) -> List[Dict]:
    items: List[Dict] = []
    try:
        root = _et.fromstring(xml_bytes)
    except _et.ParseError as exc:
        logger.warning("rss_parse_error", extra={"error": str(exc)})
        return items

    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        desc = (item.findtext("description") or "").strip()
        items.append(
            {
                "title": title,
                "url": link,
                "published": pub_date,
                "summary": desc,
                "source": "rss",
            }
        )
    return items


def fetch_ai_headlines(
    *, query: str | None = None, region: str = "IN", limit: int = 8, offline: bool = False
) -> List[Dict]:
    if offline:
        return _FALLBACK_ITEMS[:limit]

    q = query or "artificial intelligence tier-2 India Warangal"
    feeds = [
        _build_feed(q, region),
        _build_feed("AI startups Warangal OR Hyderabad", region),
    ]

    stories: List[Dict] = []
    for feed in feeds:
        try:
            req = Request(feed, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=8) as response:
                parsed = _parse_rss(response.read())
                stories.extend(parsed)
        except Exception as exc:
            logger.info("rss_fetch_failed", extra={"feed": feed, "error": str(exc)})
            continue

    if not stories:
        logger.info("rss_fallback_used")
        return _FALLBACK_ITEMS[:limit]

    return stories[:limit]


if __name__ == "__main__":
    for story in fetch_ai_headlines(limit=3, offline=True):
        print(f"- {story['title']} ({story['published']})")
