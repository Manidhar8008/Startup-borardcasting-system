# -*- coding: utf-8 -*-
"""Prompt Loader — Loads and interpolates prompt templates from /prompts/.

Supports difficulty tiers (easy/medium/hard) and variable interpolation.

Usage:
    from prompts.prompt_loader import load_prompt

    text = load_prompt("social_post.md", difficulty="hard", topic="AI agents")
"""

import logging
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger("prompts")

PROMPTS_DIR = Path(__file__).resolve().parent

# Difficulty tiers
DIFFICULTIES = ("easy", "medium", "hard")


def load_prompt(
    template_name: str,
    *,
    difficulty: str = "medium",
    **variables: Any,
) -> str:
    """Load a prompt template and interpolate variables.

    Search order:
    1. prompts/<difficulty>/<template_name>
    2. prompts/content_prompts/<template_name>  (legacy)
    3. prompts/strategy_prompts/<template_name> (legacy)
    4. prompts/research_prompts/<template_name> (legacy)
    5. prompts/<template_name>                  (direct path)

    Args:
        template_name: Template filename, e.g. 'social_post.md' or 'content_prompts/social_post.md'.
        difficulty: Prompt tier: 'easy', 'medium', or 'hard'.
        **variables: Key-value pairs to substitute into {placeholders}.

    Returns:
        The interpolated prompt string.

    Raises:
        FileNotFoundError: If no matching template is found.
    """
    # Normalize difficulty
    if difficulty not in DIFFICULTIES:
        difficulty = "medium"

    # Build search paths
    search_paths = [
        PROMPTS_DIR / difficulty / template_name,           # tiered
        PROMPTS_DIR / template_name,                         # direct path
        PROMPTS_DIR / "content_prompts" / template_name,    # legacy content
        PROMPTS_DIR / "strategy_prompts" / template_name,   # legacy strategy
        PROMPTS_DIR / "research_prompts" / template_name,   # legacy research
    ]

    for path in search_paths:
        if path.exists():
            raw = path.read_text(encoding="utf-8")
            try:
                return raw.format_map(_SafeDict(variables))
            except Exception:
                return raw

    raise FileNotFoundError(
        f"Prompt template '{template_name}' not found (difficulty='{difficulty}'). "
        f"Searched: {[str(p) for p in search_paths]}"
    )


def list_prompts(subdirectory: str = "") -> List[str]:
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
