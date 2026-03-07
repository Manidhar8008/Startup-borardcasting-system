"""YouTube scraping entrypoint for research pipeline (wraps tools_connectors.youtube_scraper)."""
from tools_connectors.youtube_scraper import fetch_latest_videos, fetch_metadata, load_channel_ids_from_env

__all__ = ["fetch_latest_videos", "fetch_metadata", "load_channel_ids_from_env"]
