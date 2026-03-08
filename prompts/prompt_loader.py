# -*- coding: utf-8 -*-
"""Prompt Loader — Loads and interpolates prompt templates from /prompts/.

Templates are markdown files with {variable} placeholders.

Usage:
    from prompts.prompt_loader import load_prompt

    text = load_prompt("content_prompts/social_post.md", topic="AI agents", brand="janani_ai")
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("prompts")

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(template_path: str, **variables: Any) -> str:
    """Load a prompt template and interpolate variables.

    Args:
        template_path: Relative path within /prompts/, e.g. 'content_prompts/social_post.md'
        **variables: Key-value pairs to substitute into {placeholders}.

    Returns:
        The interpolated prompt string.

    Raises:
        FileNotFoundError: If the template does not exist.
    """
    full_path = PROMPTS_DIR / template_path
    if not full_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {full_path}")

    raw = full_path.read_text(encoding="utf-8")

    # Interpolate variables — ignore missing placeholders gracefully
    try:
        return raw.format_map(_SafeDict(variables))
    except Exception:
        return raw


def list_prompts(subdirectory: str = "") -> list:
    """List all available prompt template files."""
    search_dir = PROMPTS_DIR / subdirectory if subdirectory else PROMPTS_DIR
    return [
        str(p.relative_to(PROMPTS_DIR))
        for p in search_dir.rglob("*.md")
        if p.name != "README.md"
    ]


class _SafeDict(dict):
    """Dict subclass that returns the key itself for missing format placeholders."""
    def __missing__(self, key):
        return f"{{{key}}}"
