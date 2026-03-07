"""Generate placeholder images for posts."""
import os
from pathlib import Path
from typing import Optional

import requests

IMAGES_DIR = Path(__file__).resolve().parent.parent / "media_assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
PLACEHOLDER_URL = "https://via.placeholder.com/1200x628.png?text=AI+Media+Engine"


def generate_placeholder(topic: str, *, dry_run: bool = True) -> Optional[str]:
    """Download a simple placeholder image and return its path."""
    filename = f"{topic[:40].replace(' ', '_')}.png"
    path = IMAGES_DIR / filename

    if dry_run:
        return str(path)

    try:
        resp = requests.get(PLACEHOLDER_URL, timeout=10)
        resp.raise_for_status()
        path.write_bytes(resp.content)
        return str(path)
    except Exception:
        return None
