"""Predict promising topics from past performance and founder ideas."""
from typing import List, Dict

from analytics_engine import viral_topics
from brain_input import brain_parser


def suggest_topics(brand: str, research_items: List[Dict]) -> List[Dict]:
    suggestions: List[Dict] = []
    # Viral topics boost
    for vt in viral_topics.top_topics(limit=5):
        suggestions.append(
            {
                "title": vt.get("topic", ""),
                "summary": vt.get("body", "") or vt.get("topic", ""),
                "source": "viral_topic",
                "suggested_score": 2.0,
                "brand": brand,
            }
        )

    # Founder ideas
    for idea in brain_parser.parse_all_inputs():
        if idea.get("brand") == brand:
            suggestions.append(
                {
                    "title": idea.get("title"),
                    "summary": idea.get("summary"),
                    "source": "founder_input",
                    "suggested_score": 1.5,
                    "brand": brand,
                }
            )

    # Research echoes (ensure brand tag)
    for item in research_items:
        if item.get("title"):
            clone = dict(item)
            clone["source"] = f"predictor_clone:{item.get('source')}"
            clone["suggested_score"] = 1.0
            clone["brand"] = brand
            suggestions.append(clone)
    return suggestions


__all__ = ["suggest_topics"]
