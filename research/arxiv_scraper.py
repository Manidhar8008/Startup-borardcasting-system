"""Minimal arXiv fetcher for AI papers."""
import logging
import xml.etree.ElementTree as _et
from typing import List, Dict
from urllib.parse import urlencode
from urllib.request import urlopen

logger = logging.getLogger("research")

ARXIV_API = "http://export.arxiv.org/api/query"

_FALLBACK = [
    {
        "title": "Alignment evaluations for small teams",
        "authors": ["Doe, A."],
        "published": "2026-02-27",
        "summary": "Proposes lightweight eval sets for domain-specific agents.",
        "link": "https://arxiv.org/abs/1234.56789",
    }
]


def _parse_entries(xml_bytes: bytes) -> List[Dict]:
    entries: List[Dict] = []
    try:
        root = _et.fromstring(xml_bytes)
    except _et.ParseError as exc:
        logger.warning("arxiv_parse_error", extra={"error": str(exc)})
        return entries

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
        published = (entry.findtext("{http://www.w3.org/2005/Atom}published") or "").strip()
        link = entry.findtext("{http://www.w3.org/2005/Atom}id") or ""
        authors = [a.text for a in entry.findall("{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name")]
        entries.append(
            {
                "title": title,
                "summary": summary,
                "published": published,
                "link": link,
                "authors": authors,
            }
        )
    return entries


def fetch_recent_papers(query: str = "artificial intelligence", *, limit: int = 5, offline: bool = False) -> List[Dict]:
    if offline:
        return _FALLBACK[:limit]

    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": limit,
    }
    url = f"{ARXIV_API}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=10) as response:
            xml_bytes = response.read()
    except Exception as exc:
        logger.info("arxiv_fetch_failed", extra={"error": str(exc)})
        return _FALLBACK[:limit]

    entries = _parse_entries(xml_bytes)
    return entries[:limit] if entries else _FALLBACK[:limit]


if __name__ == "__main__":
    for paper in fetch_recent_papers(limit=2, offline=True):
        print(paper["title"])
