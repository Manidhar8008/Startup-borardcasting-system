# -*- coding: utf-8 -*-
"""Research agent: gathers topics and signals for a brand.

v3 — Now powered by the multi-source research_pipeline.
Falls back to hardcoded topics only when all live sources fail.
"""

import logging
from typing import Dict, List

logger = logging.getLogger("research")

# Fallback topics used only when all live sources fail
_FALLBACK_TOPICS = {
    "janani_ai": [
        "AI tools for small businesses in India",
        "Vernacular AI and regional language models",
        "Low-cost automation for Tier-2 cities",
        "WhatsApp business bots for local entrepreneurs",
        "AI-powered customer support in Indian markets",
    ],
    "mw_ai_data_systems": [
        "Real-time data pipelines with Python",
        "AI-driven analytics for SMBs",
        "Building MLOps workflows on a budget",
        "Data quality automation",
        "Open-source LLMs for enterprise data",
    ],
    "mw_ai_news": [
        "Latest AI research breakthroughs",
        "Startup funding trends in AI",
        "Regulatory updates on AI in India",
        "Big Tech AI product launches",
        "Open-source model releases",
    ],
    "mw_ai_edu": [
        "Python for beginners in AI",
        "Hands-on LLM fine-tuning tutorials",
        "Prompt engineering best practices",
        "Building RAG pipelines step by step",
        "AI career roadmap for freshers",
    ],
}

_DEFAULT_FALLBACK = [
    "Artificial Intelligence trends",
    "Machine learning for startups",
    "Automation in business workflows",
    "AI ethics and responsible deployment",
    "Future of work with AI tools",
]


def _fallback_results(brand: str, topic: str = "") -> List[Dict]:
    """Generate fallback results when live pipeline fails."""
    if topic:
        return [
            {"title": f"{topic}: Key Trends", "summary": f"Current developments in {topic}.", "source": "fallback", "brand": brand},
            {"title": f"{topic}: Startup Opportunities", "summary": f"How startups can leverage {topic}.", "source": "fallback", "brand": brand},
            {"title": f"{topic}: Challenges", "summary": f"Top challenges in implementing {topic}.", "source": "fallback", "brand": brand},
        ]
    topics = _FALLBACK_TOPICS.get(brand, _DEFAULT_FALLBACK)
    return [
        {"title": t, "summary": f"Research signal: {t}. Relevant to {brand}.", "source": "fallback", "brand": brand}
        for t in topics
    ]


def gather(brand: str, *, topic: str = "", offline: bool = True) -> List[Dict]:
    """Gather research topics via multi-source pipeline.

    Falls back to hardcoded topics only when the pipeline returns nothing.
    """
    try:
        from research.research_pipeline import run_pipeline
        results = run_pipeline(
            query=topic or brand,
            brand=brand,
            offline=offline,
            limit=15,
        )
        if results:
            logger.info("Pipeline returned %d items for brand '%s'", len(results), brand)
            return results
    except Exception as exc:
        logger.warning("Research pipeline failed: %s — using fallback", exc)

    # Fallback: hardcoded topics
    results = _fallback_results(brand, topic)
    logger.info("Using fallback: %d items for brand '%s'", len(results), brand)
    return results
