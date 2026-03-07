"""Decide which platforms to use for a given content type."""
from typing import List

ROUTES = {
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
}


def route(content_type: str, *, fallback: List[str] | None = None) -> List[str]:
    return ROUTES.get(content_type, fallback or ["linkedin"])
