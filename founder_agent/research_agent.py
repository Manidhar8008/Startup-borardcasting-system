"""Research agent: gathers topics and signals for a brand."""
from typing import List, Dict
import logging

logger = logging.getLogger("research")

BRAND_TOPICS = {
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

DEFAULT_TOPICS = [
    "Artificial Intelligence trends",
    "Machine learning for startups",
    "Automation in business workflows",
    "AI ethics and responsible deployment",
    "Future of work with AI tools",
]


def gather(brand: str, *, topic: str = "", offline: bool = True) -> List[Dict]:
    """Return a list of research items for the given brand (or topic)."""
    base_topics = BRAND_TOPICS.get(brand, DEFAULT_TOPICS)

    if topic:
        results = [
            {
                "title": f"{topic}: Key Trends",
                "summary": f"An exploration of current developments in {topic}, focusing on practical applications.",
                "source": "internal",
                "brand": brand,
            },
            {
                "title": f"{topic}: Opportunities for Startups",
                "summary": f"How startups can leverage {topic} to gain a competitive edge in 2025.",
                "source": "internal",
                "brand": brand,
            },
            {
                "title": f"{topic}: Common Challenges",
                "summary": f"Top challenges practitioners face when implementing {topic} and how to overcome them.",
                "source": "internal",
                "brand": brand,
            },
        ]
        logger.info("Researched topic '%s' for brand '%s'", topic, brand)
        return results

    results = [
        {
            "title": t,
            "summary": f"Research signal on: {t}. Relevant to {brand} audience.",
            "source": "internal",
            "brand": brand,
        }
        for t in base_topics
    ]
    logger.info("Gathered %d research items for brand '%s'", len(results), brand)
    return results
