"""Parse founder inputs (notes, dumps, links, requests) into structured ideas per brand."""
import re
from pathlib import Path
from typing import Dict, List

from decision_engine.approval_queue import ApprovalQueue

BRAIN_DIR = Path(__file__).resolve().parent

BRAND_KEYWORDS = {
    "janani_ai": ["janani", "philosophy", "founder", "vision", "behavior"],
    "mw_ai_data_systems": ["data", "infra", "warehouse", "analytics", "systems"],
    "mw_ai_news": ["news", "headline", "update", "policy", "warangal", "tier-2"],
    "mw_ai_edu": ["tutorial", "edu", "student", "learn", "course", "beginner"],
}

DEFAULT_BRAND = "janani_ai"


def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]


def infer_brand(text: str, default: str = DEFAULT_BRAND) -> str:
    low = text.lower()
    for brand, kws in BRAND_KEYWORDS.items():
        if any(k in low for k in kws):
            return brand
    return default


def _idea_obj(title: str, summary: str, brand: str, source: str, content_length: str = "short") -> Dict:
    return {
        "title": title,
        "summary": summary,
        "brand": brand,
        "source": source,
        "content_length": content_length,
    }


def parse_daily_notes(path: Path | str = BRAIN_DIR / "daily_notes.md") -> List[Dict]:
    path = Path(path)
    if not path.exists():
        return []
    sections = {"ideas": [], "research": [], "content_request": []}
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        header = line.rstrip(":").lower()
        if header in sections:
            current = header
            continue
        if current:
            sections[current].append(line)

    ideas: List[Dict] = []
    for idea in sections["ideas"]:
        brand = infer_brand(idea)
        ideas.append(_idea_obj(idea, idea, brand, "brain_notes"))
    for link in sections["research"]:
        brand = infer_brand(link)
        ideas.append(_idea_obj(f"Research link", link, brand, "brain_notes_research"))
    for req in sections["content_request"]:
        brand = infer_brand(req)
        ideas.append(_idea_obj(f"Content request: {req}", req, brand, "brain_notes_request"))
    return ideas


def parse_ideas_dump(path: Path | str = BRAIN_DIR / "ideas_dump.md") -> List[Dict]:
    lines = _read_lines(Path(path))
    return [_idea_obj(line, line, infer_brand(line), "ideas_dump") for line in lines]


def parse_research_links(path: Path | str = BRAIN_DIR / "research_links.md") -> List[Dict]:
    links = _read_lines(Path(path))
    ideas: List[Dict] = []
    for link in links:
        brand = infer_brand(link)
        ideas.append(_idea_obj("Research link", link, brand, "research_links", content_length="long"))
    return ideas


def parse_content_requests(path: Path | str = BRAIN_DIR / "content_requests.md") -> List[Dict]:
    lines = _read_lines(Path(path))
    ideas: List[Dict] = []
    for line in lines:
        m = re.match(r"(janani_ai|mw_ai_data_systems|mw_ai_news|mw_ai_edu)\s+(.*)", line, flags=re.I)
        if m:
            brand = m.group(1).lower()
            rest = m.group(2).strip()
        else:
            brand = infer_brand(line)
            rest = line
        ideas.append(_idea_obj(f"Content request: {rest}", rest, brand, "content_requests"))
    return ideas


def parse_all_inputs() -> List[Dict]:
    ideas: List[Dict] = []
    ideas.extend(parse_daily_notes())
    ideas.extend(parse_ideas_dump())
    ideas.extend(parse_research_links())
    ideas.extend(parse_content_requests())
    return ideas


def ingest_to_queues():
    """Parse all inputs and push into brand idea queues."""
    ideas = parse_all_inputs()
    by_brand = {}
    for idea in ideas:
        brand = idea["brand"]
        by_brand.setdefault(brand, []).append(idea)
    for brand, items in by_brand.items():
        queue = ApprovalQueue(brand)
        for idea in items:
            queue.add_idea(idea)
    return {brand: len(items) for brand, items in by_brand.items()}


__all__ = [
    "parse_daily_notes",
    "parse_ideas_dump",
    "parse_research_links",
    "parse_content_requests",
    "parse_all_inputs",
    "ingest_to_queues",
]
