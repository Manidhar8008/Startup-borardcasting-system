# -*- coding: utf-8 -*-
"""Decide which platforms to use for a given content type.

Supports all 9 platforms: LinkedIn, Twitter, Instagram, YouTube,
Facebook, Blog, Newsletter, Podcast.
"""
from typing import List

ROUTES = {
    # Original content types
    "thread": ["twitter"],
    "insight": ["linkedin"],
    "visual": ["instagram"],
    "short_explainer": ["twitter", "linkedin"],
    "long_form": ["youtube", "linkedin"],
    "case_study": ["linkedin"],
    "tutorial": ["youtube", "linkedin"],
    "explainer": ["youtube", "twitter"],
    "blog": ["linkedin"],
    "podcast": ["youtube"],

    # New content types
    "linkedin_post": ["linkedin"],
    "twitter_thread": ["twitter"],
    "instagram_caption": ["instagram"],
    "youtube_script": ["youtube"],
    "youtube_short": ["youtube", "instagram"],
    "facebook_post": ["facebook"],
    "blog_post": ["blog", "linkedin"],
    "newsletter_draft": ["newsletter"],
    "newsletter": ["newsletter"],
    "podcast_outline": ["podcast", "youtube"],

    # Shorthand aliases
    "tweet": ["twitter"],
    "reel": ["instagram", "youtube"],
    "caption": ["instagram"],
    "article": ["blog", "linkedin"],
}


def route(content_type: str, *, fallback: List[str] | None = None) -> List[str]:
    """Return target platforms for a given content type."""
    return ROUTES.get(content_type, fallback or ["linkedin"])


def all_platforms() -> List[str]:
    """Return list of all supported platform names."""
    return ["linkedin", "twitter", "instagram", "youtube", "facebook", "blog", "newsletter", "podcast"]
