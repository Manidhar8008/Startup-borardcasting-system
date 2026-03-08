# -*- coding: utf-8 -*-
"""Content Multiplier — Transforms 1 idea into multiple platform-specific assets.

The core multiplication engine for the JAN AI Media Manager.
Takes a single idea and generates content for all supported platforms.

Usage:
    from content_engine.multiplier import multiply
    assets = multiply({"title": "AI agents", "summary": "..."}, brand="janani_ai")
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("engine")

# Platform output specs: (platform, content_type, max_count, prompt_key)
PLATFORM_SPECS = [
    ("linkedin", "linkedin_post", 10, "linkedin"),
    ("twitter", "twitter_thread", 5, "twitter"),
    ("youtube", "youtube_script", 1, "youtube"),
    ("youtube", "youtube_short", 1, "youtube_short"),
    ("podcast", "podcast_outline", 1, "podcast"),
    ("instagram", "instagram_caption", 1, "instagram"),
    ("newsletter", "newsletter_draft", 1, "newsletter"),
    ("blog", "blog_post", 1, "blog"),
    ("facebook", "facebook_post", 1, "facebook"),
]


def _build_platform_prompt(idea: Dict, platform: str, content_type: str, brand: str, index: int = 1) -> str:
    """Build an LLM prompt for a specific platform output."""
    title = idea.get("title", "AI and startups")
    summary = idea.get("summary", "")
    context = f"{title}. {summary}" if summary else title

    platform_instructions = {
        "linkedin": (
            f"Write LinkedIn post #{index} about: {context}\n"
            "Professional but human tone. Use line breaks for readability.\n"
            "Include a hook, insight, example or story, and a CTA.\n"
            "End with 3-5 relevant hashtags.\n"
            "Keep under 200 words."
        ),
        "twitter": (
            f"Write a Twitter/X thread (5 tweets) about: {context}\n"
            "Tweet 1 is the hook. Each tweet under 280 chars.\n"
            "Use 1/5, 2/5 format. Final tweet is CTA.\n"
            "Punchy, shareable, no fluff."
        ),
        "youtube": (
            f"Write a YouTube video script about: {context}\n"
            "Structure: INTRO (hook + preview), BODY (3 main points with examples), OUTRO (summary + CTA).\n"
            "Conversational, energetic. 3-5 minute script.\n"
            "Include [B-ROLL] suggestions."
        ),
        "youtube_short": (
            f"Write a 60-second YouTube Short script about: {context}\n"
            "Open with an attention hook (first 3 seconds).\n"
            "One sharp insight. Fast pace. End with CTA.\n"
            "Under 150 words."
        ),
        "podcast": (
            f"Write a podcast episode outline about: {context}\n"
            "Structure: Episode Title, 1-sentence premise, 5 talking points with sub-bullets,\n"
            "1 guest question prompt, closing thought.\n"
            "10-15 minute episode target."
        ),
        "instagram": (
            f"Write an Instagram caption about: {context}\n"
            "Start with a hook line. Use emojis strategically.\n"
            "Include a CTA. End with 10-15 hashtags.\n"
            "Under 150 words."
        ),
        "newsletter": (
            f"Write a newsletter section about: {context}\n"
            "Structure: Subject line, preview text, lead paragraph, 3 key bullet points,\n"
            "1 actionable tip, CTA with link placeholder.\n"
            "Scannable format. Under 300 words."
        ),
        "blog": (
            f"Write a blog post outline about: {context}\n"
            "Structure: Title, meta description, intro paragraph, 3-5 H2 sections with bullets,\n"
            "conclusion, CTA.\n"
            "SEO-optimized. 500-800 words."
        ),
        "facebook": (
            f"Write a Facebook post about: {context}\n"
            "Engaging, conversational tone. Use a question or story hook.\n"
            "Include emojis. End with discussion CTA.\n"
            "Under 150 words."
        ),
    }

    instruction = platform_instructions.get(platform, platform_instructions["linkedin"])

    return f"""You are JAN, the AI content engine for brand '{brand}'.
Voice: founder, startup mindset, storytelling, thought leadership.

{instruction}

Output only the content. No preamble, no explanation."""


def multiply(
    idea: Dict,
    *,
    brand: str = "janani_ai",
    platforms: Optional[List[str]] = None,
    counts: Optional[Dict[str, int]] = None,
) -> List[Dict]:
    """Transform 1 idea into multiple content assets across platforms.

    Args:
        idea: Dict with at least 'title' and optionally 'summary'.
        brand: Target brand.
        platforms: Which platforms to generate for. Default: all.
        counts: Override default counts per platform, e.g. {"linkedin": 3}.

    Returns:
        List of asset dicts with 'platform', 'content_type', 'draft', 'idea_source'.
    """
    # Import LLM router
    try:
        from ai_core.llm_router import generate
    except ImportError:
        from ai_core.llm_brain import generate_text as generate

    enabled_platforms = set(platforms or [spec[0] for spec in PLATFORM_SPECS])
    override_counts = counts or {}

    assets: List[Dict] = []
    title = idea.get("title", "Untitled")

    for platform, content_type, default_count, prompt_key in PLATFORM_SPECS:
        if platform not in enabled_platforms:
            continue

        count = override_counts.get(platform, default_count)

        for i in range(1, count + 1):
            prompt = _build_platform_prompt(idea, prompt_key, content_type, brand, index=i)

            try:
                draft = generate(prompt=prompt, temperature=0.75)
            except Exception as exc:
                logger.warning("Multiplier failed for %s #%d: %s", platform, i, exc)
                draft = f"[Generation failed for {platform} #{i}]"

            asset = {
                "platform": platform,
                "content_type": content_type,
                "index": i,
                "draft": draft,
                "idea_source": title,
                "brand": brand,
                "llm_generated": True,
            }
            assets.append(asset)
            logger.info("Generated %s #%d for idea '%s'", content_type, i, title[:40])

    logger.info("Multiplied idea '%s' into %d assets across %d platforms",
                title[:40], len(assets), len(enabled_platforms))
    return assets


def multiply_quick(
    idea: Dict,
    *,
    brand: str = "janani_ai",
) -> List[Dict]:
    """Quick multiply — generates 1 asset per platform (faster for testing)."""
    return multiply(idea, brand=brand, counts={
        "linkedin": 1, "twitter": 1, "youtube": 1, "youtube_short": 1,
        "podcast": 1, "instagram": 1, "newsletter": 1, "blog": 1, "facebook": 1,
    })


def format_multiplication_report(assets: List[Dict]) -> str:
    """Format a human-readable report of multiplied assets."""
    by_platform: Dict[str, int] = {}
    for a in assets:
        p = a.get("platform", "unknown")
        by_platform[p] = by_platform.get(p, 0) + 1

    lines = [f"\n🔄 Content Multiplication Report ({len(assets)} total assets):"]
    for platform, count in sorted(by_platform.items()):
        lines.append(f"  • {platform:<12} → {count} asset(s)")
    return "\n".join(lines)


__all__ = ["multiply", "multiply_quick", "format_multiplication_report"]
