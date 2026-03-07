"""Agent that aggregates research sources for a brand."""
import os
import logging
from typing import List, Dict

from research import ai_news_scraper, arxiv_scraper, github_ai_trends, youtube_scraper
from tools_connectors import notebooklm_connector, perplexity_connector


def gather(brand: str, *, offline: bool = False) -> List[Dict]:
    logger = logging.getLogger("research")
    region = os.getenv("REGION", "IN")
    city = os.getenv("CITY", "Warangal")
    items: List[Dict] = []

    news = ai_news_scraper.fetch_ai_headlines(region=region, query=f"AI {city}", offline=offline)
    papers = arxiv_scraper.fetch_recent_papers(query="artificial intelligence", limit=3, offline=offline)
    repos = github_ai_trends.fetch_trending(limit=3, offline=offline)

    perplexity_prompt = f"Top AI/startup stories for {city} founders ({brand}) this week."
    px = perplexity_connector.ask_perplexity(perplexity_prompt)
    notebook_summary = notebooklm_connector.summarize_notes([i.get("summary", "") for i in news[:2]])
    channel_ids = youtube_scraper.load_channel_ids_from_env()
    yt_items = youtube_scraper.fetch_latest_videos(channel_ids, limit=2, offline=offline) if channel_ids else []

    for story in news:
        items.append({"title": story.get("title"), "summary": story.get("summary"), "source": "news"})
    for paper in papers:
        items.append({"title": paper.get("title"), "summary": paper.get("summary"), "source": "arxiv"})
    for repo in repos:
        items.append({"title": repo.get("title"), "summary": repo.get("summary"), "source": "github"})
    if px:
        items.append({"title": "Perplexity pulse", "summary": px.get("answer", ""), "source": "perplexity"})
    if notebook_summary:
        items.append({"title": "NotebookLM notes", "summary": notebook_summary.get("summary", ""), "source": "notebooklm"})
    for yt in yt_items:
        items.append({"title": yt.get("title"), "summary": "Latest video", "source": "youtube"})

    logger.info("research_collected", extra={"brand": brand, "items": len(items)})
    return items
