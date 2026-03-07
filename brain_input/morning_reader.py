"""
morning_reader.py — Parses brain_input/morning_notes.md into structured data for JAN.

Returns:
    {
        "focus_topics": [...],
        "tasks": [...],
        "content_goals": [...]
    }
"""

import re
from pathlib import Path
from typing import Dict, List

NOTES_PATH = Path(__file__).resolve().parent / "morning_notes.md"

# Section header aliases
_SECTION_MAP = {
    "focus":         "focus_topics",
    "tasks":         "tasks",
    "content goals": "content_goals",
    "content_goals": "content_goals",
    "notes":         "notes",
}


def read_morning_notes(path: Path | str = NOTES_PATH) -> Dict[str, List[str]]:
    """
    Parse morning_notes.md and return structured dict.

    Keys: focus_topics, tasks, content_goals, notes (all lists of strings).
    """
    result: Dict[str, List[str]] = {
        "focus_topics": [],
        "tasks": [],
        "content_goals": [],
        "notes": [],
    }

    path = Path(path)
    if not path.exists():
        return result

    text = path.read_text(encoding="utf-8")
    current_section: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Skip empty lines and markdown-comment lines
        if not line or line.startswith("#"):
            # But '#'-prefixed section headers like "# Focus:" are handled below
            # Strip '#' and check if it's a section header
            stripped = line.lstrip("#").strip()
        else:
            stripped = line

        # Detect section headers  e.g. "Focus:", "Tasks:", "Content Goals:"
        header_candidate = stripped.rstrip(":").lower()
        if header_candidate in _SECTION_MAP and stripped.endswith(":"):
            current_section = _SECTION_MAP[header_candidate]
            continue

        if current_section is None:
            # Could be an inline "Focus: ..." line
            for key, mapped in _SECTION_MAP.items():
                m = re.match(rf"^{re.escape(key)}\s*:\s*(.+)", stripped, flags=re.IGNORECASE)
                if m:
                    result[mapped].append(m.group(1).strip())
                    break
            continue

        # Strip leading list markers (-, *, •, digits.)
        content = re.sub(r"^[-*•]\s+", "", stripped)
        content = re.sub(r"^\d+\.\s+", "", content)
        if content:
            result[current_section].append(content)

    return result


def format_briefing(notes: Dict[str, List[str]]) -> str:
    """Pretty-print the parsed morning notes."""
    lines = ["\n🌅  Morning Briefing — Founder's Notes:"]

    if notes.get("focus_topics"):
        lines.append("\n  🎯 Focus Topics:")
        for t in notes["focus_topics"]:
            lines.append(f"     • {t}")

    if notes.get("tasks"):
        lines.append("\n  ✅ Today's Tasks:")
        for t in notes["tasks"]:
            lines.append(f"     • {t}")

    if notes.get("content_goals"):
        lines.append("\n  📣 Content Goals:")
        for g in notes["content_goals"]:
            lines.append(f"     • {g}")

    if notes.get("notes"):
        lines.append("\n  📝 Notes:")
        for n in notes["notes"]:
            lines.append(f"     • {n}")

    return "\n".join(lines)


__all__ = ["read_morning_notes", "format_briefing"]
