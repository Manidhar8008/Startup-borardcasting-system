"""Optimize drafts based on brand tone and structure."""
from textwrap import shorten
from typing import Dict


def optimize_draft(draft: Dict, structure: Dict) -> Dict:
    tone = ", ".join(structure.get("tone", []))
    cta_style = structure.get("cta_style", draft.get("sections", {}).get("cta", ""))

    # Shorten core sections to keep concise
    optimized = dict(draft)
    sections = optimized.get("sections", {})
    if "hook" in sections:
        sections["hook"] = shorten(sections["hook"], width=140, placeholder="…")
    if "insight" in sections:
        sections["insight"] = shorten(sections["insight"], width=200, placeholder="…")
    sections["cta"] = sections.get("cta") or cta_style
    optimized["sections"] = sections

    # Rebuild draft text
    lines = [
        f"Hook: {sections.get('hook', '')}",
        f"Insight: {sections.get('insight', '')}",
        f"Example: {sections.get('example', '')}",
        f"CTA: {sections.get('cta', '')} ({tone})",
    ]
    optimized["draft"] = "\n".join(lines).strip()
    return optimized


__all__ = ["optimize_draft"]
