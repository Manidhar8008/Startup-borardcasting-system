"""
llm_brain.py — Local LLM interface via Ollama.

Sends prompts to a locally running Ollama instance and returns generated text.
Falls back to a stub response if Ollama is unavailable so the pipeline never crashes.
"""

import json
import logging
import requests
from typing import Optional

logger = logging.getLogger("engine")

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"


def generate_text(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    timeout: tuple = (3, 120),
    temperature: float = 0.7,
) -> str:
    """
    Send a prompt to the local Ollama API and return the full generated text.

    Args:
        prompt: The instruction / content prompt.
        model: Ollama model name (default: llama3).
        timeout: HTTP timeout in seconds.
        temperature: Sampling temperature.

    Returns:
        Generated text string. On any error, returns a clearly labelled stub.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": temperature},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout, stream=True)  # (connect_timeout, read_timeout)
        response.raise_for_status()

        parts = []
        for raw_line in response.iter_lines():
            if not raw_line:
                continue
            try:
                chunk = json.loads(raw_line)
                parts.append(chunk.get("response", ""))
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue

        text = "".join(parts).strip()
        logger.info("LLM generated %d chars for prompt[:60]='%s'", len(text), prompt[:60])
        return text if text else _stub_response(prompt)

    except requests.exceptions.ConnectionError:
        logger.warning("Ollama not reachable at %s — using stub response.", OLLAMA_URL)
        return _stub_response(prompt)
    except Exception as exc:
        logger.error("LLM error: %s", exc)
        return _stub_response(prompt)


def _stub_response(prompt: str) -> str:
    """Fallback stub when Ollama is offline — returns a formatted placeholder."""
    # Extract a short topic hint from the prompt for the stub
    lines = [ln.strip() for ln in prompt.splitlines() if ln.strip()]
    hint = lines[-1] if lines else "AI & startups"
    return (
        f"Hook: Every great startup begins with one sharp insight. Yours is about {hint}.\n\n"
        f"Insight: The intersection of AI and entrepreneurship is creating unprecedented "
        f"opportunities for builders willing to move fast and learn faster.\n\n"
        f"Example: Founders in Tier-2 India are using local LLMs to automate workflows "
        f"that previously required entire teams — at a fraction of the cost.\n\n"
        f"CTA: What's one workflow in your business you could hand off to an AI agent this week?"
        f" Drop your answer below 👇"
    )


__all__ = ["generate_text"]
