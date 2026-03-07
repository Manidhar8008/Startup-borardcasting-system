"""Thin wrapper for NotebookLM interactions (stub-friendly)."""
import os
from typing import List, Dict


class NotebookLMClient:
    def __init__(self, *, project: str | None = None):
        self.project = project or os.getenv("NOTEBOOKLM_PROJECT", "default")

    def summarize(self, notes: List[str]) -> Dict:
        """Return a deterministic summary stub. Replace with real API calls when available."""
        combined = " ".join(notes)
        preview = combined[:160] + ("..." if len(combined) > 160 else "")
        return {
            "project": self.project,
            "summary": f"NotebookLM summary for {len(notes)} notes: {preview}",
        }

    def flashcard(self, notes: List[str]) -> Dict:
        return {
            "project": self.project,
            "cards": [{"q": "Key idea?", "a": notes[0] if notes else ""}],
        }


def summarize_notes(notes: List[str], project: str | None = None) -> Dict:
    return NotebookLMClient(project=project).summarize(notes)
