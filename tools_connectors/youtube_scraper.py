"""Fetch basic YouTube metadata and recent videos via public RSS feeds."""
import json
import logging
import os
import xml.etree.ElementTree as _et
from typing import Dict, List
from urllib.request import urlopen

logger = logging.getLogger("research")

_SAMPLE = {
    "title": "AI demo day highlights",
    "channel": "Startup Broadcasting",
    "description": "Highlights from the latest AI demo day.",
}


def fetch_metadata(video_id: str, *, offline: bool = False) -> Dict:
    if offline:
        return {**_SAMPLE, "video_id": video_id}

    oembed = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        with urlopen(oembed, timeout=6) as response:
            data = json.loads(response.read())
            return {
                "video_id": video_id,
                "title": data.get("title", ""),
                "channel": data.get("author_name", ""),
                "description": data.get("title", ""),
            }
    except Exception as exc:
        logger.info("youtube_metadata_failed", extra={"error": str(exc)})
        return {**_SAMPLE, "video_id": video_id}


def fetch_latest_videos(channel_ids: List[str], *, limit: int = 3, offline: bool = False) -> List[Dict]:
    results: List[Dict] = []
    if offline:
        return [{**_SAMPLE, "video_id": "offline"}]

    for cid in channel_ids:
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
        try:
            with urlopen(feed_url, timeout=8) as resp:
                xml_bytes = resp.read()
            root = _et.fromstring(xml_bytes)
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry")[:limit]:
                title = entry.findtext("{http://www.w3.org/2005/Atom}title") or ""
                video_id = entry.findtext("{http://www.youtube.com/xml/schemas/2015}videoId") or ""
                results.append({"title": title, "video_id": video_id, "channel": cid})
        except Exception as exc:
            logger.info("youtube_feed_failed", extra={"channel": cid, "error": str(exc)})
            continue
    return results[:limit]


def fetch_captions(video_id: str) -> Dict:
    """Placeholder that signals captions are not yet implemented."""
    return {
        "video_id": video_id,
        "captions": None,
        "note": "Captions fetch not implemented in stub.",
    }


def load_channel_ids_from_env() -> List[str]:
    raw = os.getenv("YOUTUBE_CHANNEL_IDS", "")
    return [cid.strip() for cid in raw.split(",") if cid.strip()]
