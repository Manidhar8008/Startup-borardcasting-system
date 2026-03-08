# -*- coding: utf-8 -*-
"""Podcast publishing helper — generates outlines, show notes, and episode metadata."""
from typing import Dict


def format_episode(text: str, *, title: str = "") -> Dict:
    lines = [ln.strip() for ln in text.strip().split("\n") if ln.strip()]
    return {
        "episode_title": title or lines[0][:100] if lines else "AI Insights",
        "talking_points": lines[1:6] if len(lines) > 1 else lines,
        "show_notes": text.strip()[:2000],
        "estimated_minutes": max(5, len(text.split()) // 130),
    }


def publish_podcast(text: str, *, title: str = "", dry_run: bool = True) -> Dict:
    formatted = format_episode(text, title=title)
    if dry_run:
        return {"platform": "podcast", "status": "dry_run", **formatted}
    # Future: integrate with podcast hosting API
    return {"platform": "podcast", "status": "queued", **formatted}
