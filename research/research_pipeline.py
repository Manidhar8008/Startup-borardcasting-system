# -*- coding: utf-8 -*-
"""Research Pipeline — Multi-source research orchestrator.

Merges results from RSS, Perplexity, NotebookLM MCP, YouTube scraper,
and brain input into a unified, deduplicated, ranked topic list.

Usage:
    from research.research_pipeline import run_pipeline
    results = run_pipeline("AI agents", brand="janani_ai")
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("research")


def _fetch_rss(query: str, limit: int = 5, offline: bool = False) -> List[Dict]:
    """Fetch headlines from Google News RSS."""
    try:
        from research.ai_news_scraper import fetch_ai_headlines
        items = fetch_ai_headlines(query=query, limit=limit, offline=offline)
        return [
            {
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "source": f"rss:{item.get('source', 'google_news')}",
                "url": item.get("url", ""),
                "published": item.get("published", ""),
            }
            for item in items
        ]
    except Exception as exc:
        logger.warning("RSS fetch failed: %s", exc)
        return []


def _fetch_perplexity(query: str, brand: str) -> List[Dict]:
    """Fetch research via Perplexity API."""
    try:
        from tools_connectors.perplexity_connector import ask_perplexity
        result = ask_perplexity(f"Latest trends and insights on: {query}. Focus on {brand} audience.")
        answer = result.get("answer", "")
        if not answer or "placeholder" in answer.lower() or "missing" in answer.lower():
            return []
        # Parse the answer into individual topic ideas
        ideas = []
        for line in answer.split("\n"):
            line = line.strip().lstrip("-•*0123456789.) ")
            if len(line) > 15:
                ideas.append({
                    "title": line[:120],
                    "summary": line,
                    "source": "perplexity",
                })
        return ideas[:5]
    except Exception as exc:
        logger.warning("Perplexity fetch failed: %s", exc)
        return []


def _fetch_notebooklm(query: str) -> List[Dict]:
    """Query NotebookLM MCP for relevant source content."""
    try:
        from agents.mcp_tools import call_tool, is_available
        if not is_available():
            return []
        # List notebooks and query the first relevant one
        notebooks = call_tool("notebook_list", max_results=5)
        if not isinstance(notebooks, dict) or "error" in notebooks:
            return []
        nb_list = notebooks.get("notebooks", [])
        if not nb_list:
            return []
        # Query the first notebook for topic ideas
        nb_id = nb_list[0].get("id", "")
        if not nb_id:
            return []
        result = call_tool("notebook_query", notebook_id=nb_id, query=f"Key insights about: {query}")
        if isinstance(result, dict) and result.get("answer"):
            answer = result["answer"]
            ideas = []
            for line in answer.split("\n"):
                line = line.strip().lstrip("-•*0123456789.) ")
                if len(line) > 15:
                    ideas.append({
                        "title": line[:120],
                        "summary": line,
                        "source": "notebooklm",
                    })
            return ideas[:5]
        return []
    except Exception as exc:
        logger.warning("NotebookLM fetch failed: %s", exc)
        return []


def _fetch_brain_input(brand: str) -> List[Dict]:
    """Collect ideas from founder brain input files."""
    try:
        from brain_input.brain_parser import parse_all_inputs
        raw_ideas = parse_all_inputs()
        return [
            {
                "title": idea.get("title", ""),
                "summary": idea.get("summary", ""),
                "source": f"brain:{idea.get('source', 'notes')}",
                "brand": idea.get("brand", brand),
            }
            for idea in raw_ideas
            if idea.get("brand", brand) == brand
        ]
    except Exception as exc:
        logger.warning("Brain input fetch failed: %s", exc)
        return []


def _fetch_youtube(query: str, limit: int = 3) -> List[Dict]:
    """Fetch research from YouTube scraper."""
    try:
        from tools_connectors.youtube_scraper import scrape_topics
        items = scrape_topics(query=query, limit=limit)
        return [
            {
                "title": item.get("title", ""),
                "summary": item.get("summary", item.get("description", "")),
                "source": "youtube",
                "url": item.get("url", ""),
            }
            for item in items
        ]
    except Exception as exc:
        logger.warning("YouTube fetch failed: %s", exc)
        return []


def _deduplicate(items: List[Dict]) -> List[Dict]:
    """Remove near-duplicate topics by normalized title matching."""
    seen = set()
    unique = []
    for item in items:
        key = item.get("title", "").lower().strip()[:60]
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def run_pipeline(
    query: str = "",
    *,
    brand: str = "janani_ai",
    offline: bool = False,
    sources: Optional[List[str]] = None,
    limit: int = 15,
) -> List[Dict]:
    """Run the full multi-source research pipeline.

    Args:
        query: Research topic or keyword.
        brand: Target brand for relevance filtering.
        offline: If True, skip live API calls (RSS offline + brain only).
        sources: Which sources to use. Default: all. Options: rss, perplexity, notebooklm, brain, youtube.
        limit: Max number of results to return.

    Returns:
        Deduplicated, merged list of topic dicts with title, summary, source.
    """
    enabled = set(sources or ["rss", "perplexity", "notebooklm", "brain", "youtube"])
    all_items: List[Dict] = []

    logger.info("Research pipeline: query='%s' brand='%s' sources=%s offline=%s", query, brand, enabled, offline)

    # 1. Brain input (always available)
    if "brain" in enabled:
        brain_items = _fetch_brain_input(brand)
        all_items.extend(brain_items)
        logger.info("Brain input: %d items", len(brain_items))

    # 2. RSS (works offline with fallback)
    if "rss" in enabled:
        rss_items = _fetch_rss(query, limit=8, offline=offline)
        all_items.extend(rss_items)
        logger.info("RSS: %d items", len(rss_items))

    # 3. Live sources (skip if offline)
    if not offline:
        if "perplexity" in enabled:
            perp_items = _fetch_perplexity(query, brand)
            all_items.extend(perp_items)
            logger.info("Perplexity: %d items", len(perp_items))

        if "notebooklm" in enabled:
            nlm_items = _fetch_notebooklm(query)
            all_items.extend(nlm_items)
            logger.info("NotebookLM: %d items", len(nlm_items))

        if "youtube" in enabled:
            yt_items = _fetch_youtube(query, limit=3)
            all_items.extend(yt_items)
            logger.info("YouTube: %d items", len(yt_items))

    # 4. Deduplicate and tag with brand
    items = _deduplicate(all_items)
    for item in items:
        item.setdefault("brand", brand)

    logger.info("Research pipeline complete: %d unique items (from %d raw)", len(items), len(all_items))
    return items[:limit]


__all__ = ["run_pipeline"]
