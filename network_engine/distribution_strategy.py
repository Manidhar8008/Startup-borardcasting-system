"""Define cross-brand distribution strategy for the network."""
from typing import List

ROUTES = {
    "janani_ai": ["linkedin", "blog"],
    "mw_ai_data_systems": ["linkedin", "twitter"],
    "mw_ai_news": ["twitter", "instagram"],
    "mw_ai_edu": ["youtube", "blog"],
}


def route_for_brand(brand: str) -> List[str]:
    return ROUTES.get(brand, ["linkedin"])


def is_core_brand(brand: str) -> bool:
    return brand in {"janani_ai", "mw_ai_data_systems"}


def is_distribution_brand(brand: str) -> bool:
    return brand in {"mw_ai_news", "mw_ai_edu"}
