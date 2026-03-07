"""JAN Research Agent: gathers topics for a given subject using existing founder_agent infrastructure."""
from typing import List, Dict

from founder_agent import research_agent as _core_research


def run(topic: str, brand: str = "janani_ai") -> List[Dict]:
    """
    Gather research topics.
    Returns a list of dicts with 'title' and 'summary'.
    """
    results = _core_research.gather(brand, topic=topic, offline=True)
    return results


def format_output(results: List[Dict]) -> str:
    lines = [f"\n🔍 Research Results ({len(results)} found):"]
    for i, r in enumerate(results, 1):
        lines.append(f"  {i}. {r['title']}")
        lines.append(f"     {r['summary']}")
    return "\n".join(lines)
