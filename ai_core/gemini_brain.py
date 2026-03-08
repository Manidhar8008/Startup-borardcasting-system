# -*- coding: utf-8 -*-
"""Gemini Brain — Google Gemini API client for the JAN AI Media Manager.

Provides LLM text generation via the Gemini API.
Falls back gracefully when API key is missing.

Usage:
    from ai_core.gemini_brain import generate_text
    result = generate_text("Write a LinkedIn post about AI agents")
"""

import logging
import os
from pathlib import Path
from typing import Optional

# Auto-load .env file
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

logger = logging.getLogger("engine")

DEFAULT_MODEL = "gemini-2.0-flash"


def _get_client():
    """Lazy-load the Gemini client to avoid import errors when not installed."""
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        client = genai.Client(api_key=api_key)
        return client
    except ImportError:
        logger.warning("google-genai not installed. Run: pip install google-genai")
        return None


def generate_text(
    prompt: str,
    *,
    model: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """Generate text using the Gemini API.

    Args:
        prompt: The instruction/content prompt.
        model: Gemini model name (default from env or gemini-2.0-flash).
        temperature: Sampling temperature.
        max_tokens: Maximum output tokens.

    Returns:
        Generated text string. Empty string on failure.
    """
    model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    client = _get_client()

    if client is None:
        logger.info("Gemini unavailable — no API key or SDK not installed.")
        return ""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        text = response.text.strip() if response.text else ""
        logger.info("Gemini generated %d chars (model=%s)", len(text), model)
        return text

    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return ""


def expand_idea(idea: str, *, brand: str = "janani_ai") -> str:
    """Use Gemini to expand a short idea into a detailed content brief."""
    prompt = f"""You are JAN, content strategist for brand '{brand}'.

Take this brief idea and expand it into a detailed content brief with:
1. Core message (1 sentence)
2. Target audience
3. Key talking points (3-5 bullets)
4. Suggested platforms
5. Content angle/hook

Idea: {idea}

Output only the brief. No preamble."""
    return generate_text(prompt, temperature=0.6)


def is_available() -> bool:
    """Check if Gemini API is configured and accessible."""
    return _get_client() is not None


__all__ = ["generate_text", "expand_idea", "is_available"]
