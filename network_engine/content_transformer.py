# -*- coding: utf-8 -*-
"""Transform long-form content into platform-specific formats.

Expanded to support 9 platforms: LinkedIn, Twitter, Instagram, YouTube,
YouTube Short, Facebook, Blog, Newsletter, Podcast.
"""

from textwrap import wrap
from typing import Dict


def _sanitize(text: str) -> str:
    return text.strip().replace("\r\n", "\n")


# ── Existing platforms (upgraded) ──────────────────────────────────────────────

def generate_linkedin_post(content: str, *, brand: str) -> Dict:
    """Format content for LinkedIn with hashtags and structure."""
    text = _sanitize(content)
    # Keep paragraph structure for LinkedIn
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    body = "\n\n".join(paragraphs[:5])
    if len(body) > 2800:
        body = body[:2800] + "..."
    hashtags = f"\n\n#AI #{brand} #StartupLife #ContentCreator #MediaManager"
    return {
        "platform": "linkedin",
        "brand": brand,
        "text": f"{body}{hashtags}",
        "char_count": len(body),
    }


def generate_twitter_thread(content: str, *, brand: str) -> Dict:
    """Format content as a numbered Twitter thread."""
    text = _sanitize(content).replace("\n", " ")
    chunks = wrap(text, width=240)[:8]
    thread = [f"{idx + 1}/{len(chunks)} {chunk}" for idx, chunk in enumerate(chunks)]
    return {
        "platform": "twitter",
        "brand": brand,
        "thread": thread,
        "tweet_count": len(thread),
    }


def generate_instagram_caption(content: str, *, brand: str) -> Dict:
    """Format content as an Instagram caption with emojis and hashtags."""
    text = _sanitize(content)
    caption = text[:2000]
    hashtags = (
        f"\n\n.\n.\n.\n"
        f"#{brand} #AI #ContentCreator #StartupLife #TechFounder "
        f"#MediaManager #Innovation #Automation #CreatorEconomy #AITools"
    )
    return {
        "platform": "instagram",
        "brand": brand,
        "caption": f"{caption}{hashtags}",
        "char_count": len(caption),
    }


def generate_youtube_script(content: str, *, brand: str) -> Dict:
    """Format content as a structured YouTube video script."""
    text = _sanitize(content)
    if "INTRO:" not in text.upper():
        intro = f"Welcome back! Today we're diving into something exciting.\n\n{text[:200]}"
        body = text[:2000]
        outro = f"\n\nIf this was valuable, smash that subscribe button. See you in the next one! — {brand}"
        script = f"INTRO:\n{intro}\n\nBODY:\n{body}\n\nOUTRO:\n{outro}"
    else:
        script = text[:3000]
    return {
        "platform": "youtube",
        "brand": brand,
        "script": script,
        "estimated_minutes": max(1, len(script.split()) // 150),
    }


# ── New platforms ──────────────────────────────────────────────────────────────

def generate_youtube_short_script(content: str, *, brand: str) -> Dict:
    """Format content as a 60-second YouTube Short script."""
    text = _sanitize(content).replace("\n", " ")
    # YouTube Shorts: ~150 words for 60 seconds
    words = text.split()[:150]
    script = " ".join(words)
    return {
        "platform": "youtube",
        "content_type": "short",
        "brand": brand,
        "script": script,
        "word_count": len(words),
        "estimated_seconds": min(len(words) * 0.4, 60),
    }


def generate_facebook_post(content: str, *, brand: str) -> Dict:
    """Format content for Facebook with engagement-friendly structure."""
    text = _sanitize(content)
    # Facebook: conversational, emoji-friendly, 150-300 words ideal
    post = text[:1500]
    return {
        "platform": "facebook",
        "brand": brand,
        "text": post,
        "char_count": len(post),
    }


def generate_blog_draft(content: str, *, brand: str) -> Dict:
    """Format content as a blog post draft with SEO structure."""
    text = _sanitize(content)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Auto-generate meta description from first paragraph
    meta = paragraphs[0][:155] + "..." if paragraphs else text[:155] + "..."

    return {
        "platform": "blog",
        "brand": brand,
        "body": text[:5000],
        "meta_description": meta,
        "word_count": len(text.split()),
    }


def generate_newsletter_section(content: str, *, brand: str) -> Dict:
    """Format content as a newsletter-ready section."""
    text = _sanitize(content)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    lead = paragraphs[0] if paragraphs else text[:200]
    body = "\n\n".join(paragraphs[1:4]) if len(paragraphs) > 1 else text[:500]

    return {
        "platform": "newsletter",
        "brand": brand,
        "subject_line": text.split("\n")[0][:80] if text else "This week in AI",
        "preview_text": lead[:120],
        "lead": lead,
        "body": body,
        "word_count": len(text.split()),
    }


def generate_podcast_outline(content: str, *, brand: str) -> Dict:
    """Format content as a podcast episode outline."""
    text = _sanitize(content)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    title = lines[0] if lines else "AI Insights Episode"
    talking_points = lines[1:6] if len(lines) > 1 else [text[:200]]

    return {
        "platform": "podcast",
        "brand": brand,
        "episode_title": title[:100],
        "talking_points": talking_points,
        "estimated_minutes": max(5, len(text.split()) // 130),
    }


# ── Universal transformer ────────────────────────────────────────────────────

TRANSFORMERS = {
    "linkedin": generate_linkedin_post,
    "twitter": generate_twitter_thread,
    "instagram": generate_instagram_caption,
    "youtube": generate_youtube_script,
    "youtube_short": generate_youtube_short_script,
    "facebook": generate_facebook_post,
    "blog": generate_blog_draft,
    "newsletter": generate_newsletter_section,
    "podcast": generate_podcast_outline,
}


def transform(content: str, platform: str, *, brand: str = "janani_ai") -> Dict:
    """Transform content for any supported platform.

    Args:
        content: Raw content text.
        platform: Target platform name.
        brand: Brand identifier.

    Returns:
        Platform-formatted content dict.
    """
    transformer = TRANSFORMERS.get(platform, generate_linkedin_post)
    return transformer(content, brand=brand)


def supported_platforms() -> list:
    """List all supported platform names."""
    return list(TRANSFORMERS.keys())
