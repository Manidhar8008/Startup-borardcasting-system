# -*- coding: utf-8 -*-
"""LLM Router — Selects the best LLM provider for content generation.

Routes requests to Gemini (primary) or Ollama (fallback) based on
configuration and availability.

Usage:
    from ai_core.llm_router import generate

    text = generate("Write a LinkedIn post", provider="auto")
"""

import logging
import os
from typing import Optional

logger = logging.getLogger("engine")

# Provider constants
PROVIDER_AUTO = "auto"
PROVIDER_GEMINI = "gemini"
PROVIDER_OLLAMA = "ollama"

VALID_PROVIDERS = {PROVIDER_AUTO, PROVIDER_GEMINI, PROVIDER_OLLAMA}


def generate(
    prompt: str,
    *,
    provider: str = "",
    model: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """Generate text using the best available LLM.

    Provider selection:
      - "auto" (default): Try Gemini first, fall back to Ollama
      - "gemini": Gemini API only (returns empty if unavailable)
      - "ollama": Local Ollama only

    Args:
        prompt: The instruction/content prompt.
        provider: LLM provider to use (auto|gemini|ollama).
        model: Model name override.
        temperature: Sampling temperature.
        max_tokens: Maximum output tokens.

    Returns:
        Generated text string.
    """
    # Cost control check
    try:
        from ai_core.cost_controller import get_controller, CostLimitExceeded
        cc = get_controller()
        cc.check()
    except CostLimitExceeded as exc:
        logger.error("Cost limit exceeded: %s", exc)
        return f"[Cost limit exceeded: {exc}]"
    except ImportError:
        cc = None

    provider = provider or os.getenv("LLM_PROVIDER", PROVIDER_AUTO).lower()
    if provider not in VALID_PROVIDERS:
        logger.warning("Unknown provider '%s', defaulting to 'auto'", provider)
        provider = PROVIDER_AUTO

    result = ""
    if provider == PROVIDER_GEMINI:
        result = _call_gemini(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
    elif provider == PROVIDER_OLLAMA:
        result = _call_ollama(prompt, model=model, temperature=temperature)
    else:
        # AUTO: Gemini → Ollama fallback
        result = _call_gemini(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
        if not result:
            logger.info("Gemini unavailable, falling back to Ollama")
            result = _call_ollama(prompt, model=model, temperature=temperature)

    # Record usage
    if cc and result:
        estimated_tokens = len(prompt.split()) + len(result.split())
        cc.record_call(tokens=estimated_tokens)

    return result


def _call_gemini(prompt: str, *, model: str = "", temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """Call Gemini API."""
    try:
        from ai_core.gemini_brain import generate_text as gemini_generate
        return gemini_generate(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
    except Exception as exc:
        logger.warning("Gemini call failed: %s", exc)
        return ""


def _call_ollama(prompt: str, *, model: str = "", temperature: float = 0.7) -> str:
    """Call local Ollama."""
    try:
        from ai_core.llm_brain import generate_text as ollama_generate
        return ollama_generate(prompt, model=model or "llama3", temperature=temperature)
    except Exception as exc:
        logger.warning("Ollama call failed: %s", exc)
        return f"[LLM unavailable] Prompt: {prompt[:100]}..."


def get_active_provider() -> str:
    """Return which provider is currently active."""
    from ai_core.gemini_brain import is_available as gemini_available
    provider = os.getenv("LLM_PROVIDER", PROVIDER_AUTO).lower()

    if provider == PROVIDER_GEMINI:
        return "gemini" if gemini_available() else "gemini (unavailable)"
    if provider == PROVIDER_OLLAMA:
        return "ollama"
    # Auto
    return "gemini (auto)" if gemini_available() else "ollama (auto-fallback)"


__all__ = ["generate", "get_active_provider", "PROVIDER_AUTO", "PROVIDER_GEMINI", "PROVIDER_OLLAMA"]
