# -*- coding: utf-8 -*-
"""
ai_core/workflow_interpreter.py — Natural language intent parser for JAN.

Converts a free-text user message into a structured workflow intent dict
that execute_workflow() in JanManager can act on.

Strategy:
  1. Try LLM-based extraction (rich, context-aware, handles phrasing variations)
  2. If Ollama is offline or LLM output is unparseable, fall back to regex
  3. Always pass output through _validate() to normalise and clamp values

Output schema:
{
    "intent":    str,        # content_generation | research | planning | briefing | unknown
    "topic":     str,        # extracted topic / subject (clean — no brand/lang fragments)
    "formats":   list[str],  # e.g. ["short_video", "thread", "insight", "tutorial"]
    "brand":     str,        # one of the four supported brands
    "quantity":  int,        # 1-10, how many content pieces
    "platforms": list[str],  # e.g. ["youtube", "twitter", "linkedin"]
    "language":  str,        # e.g. "telugu", "hindi", "english" — "" when not specified
    "raw":       str,        # original message unchanged
}
"""

import json
import logging
import re
from typing import Dict, List, Optional

from ai_core import llm_brain

logger = logging.getLogger("engine")

# ── Canonical value sets ────────────────────────────────────────────────────────

VALID_INTENTS   = {"content_generation", "research", "planning", "briefing", "unknown"}
VALID_FORMATS   = {"thread", "insight", "short_video", "tutorial",
                   "long_form", "case_study", "short_explainer"}
VALID_BRANDS    = {"janani_ai", "mw_ai_data_systems", "mw_ai_news", "mw_ai_edu"}
VALID_PLATFORMS = {"twitter", "linkedin", "youtube", "instagram"}

# ── Keyword → canonical value maps ─────────────────────────────────────────────

_FORMAT_MAP: Dict[str, str] = {
    "reel":              "short_video",
    "reels":             "short_video",
    "short":             "short_video",
    "shorts":            "short_video",
    "short video":       "short_video",
    "thread":            "thread",
    "threads":           "thread",
    "tweet":             "thread",
    "tweets":            "thread",
    "post":              "insight",
    "posts":             "insight",
    "insight":           "insight",
    "insights":          "insight",
    "article":           "long_form",
    "blog":              "long_form",
    "long form":         "long_form",
    "tutorial":          "tutorial",
    "tutorials":         "tutorial",
    "guide":             "tutorial",
    "case study":        "case_study",
    "case_study":        "case_study",
    "explainer":         "short_explainer",
    "explainers":        "short_explainer",
    "short explainer":   "short_explainer",
    "script":            "long_form",
    "scripts":           "long_form",
    "video":             "long_form",
    "videos":            "long_form",
}

_PLATFORM_MAP: Dict[str, str] = {
    "youtube":   "youtube",
    "yt":        "youtube",
    "twitter":   "twitter",
    "x":         "twitter",
    "linkedin":  "linkedin",
    "instagram": "instagram",
    "ig":        "instagram",
}

# Brand map — also includes URL-style variants users type (e.g. "mw.ai edu.org")
_BRAND_MAP: Dict[str, str] = {
    "janani":                "janani_ai",
    "janani ai":             "janani_ai",
    "janani_ai":             "janani_ai",
    "mw data":               "mw_ai_data_systems",
    "mw data systems":       "mw_ai_data_systems",
    "mw_ai_data":            "mw_ai_data_systems",
    "mw_ai_data_systems":    "mw_ai_data_systems",
    "mw ai data":            "mw_ai_data_systems",
    "mw news":               "mw_ai_news",
    "mw_ai_news":            "mw_ai_news",
    "mw ai news":            "mw_ai_news",
    "mw edu":                "mw_ai_edu",
    "mw_ai_edu":             "mw_ai_edu",
    "mw ai edu":             "mw_ai_edu",
    "mw.ai edu.org":         "mw_ai_edu",   # URL-style variant
    "mw.ai edu":             "mw_ai_edu",
    "mw.ai data.org":        "mw_ai_data_systems",
    "mw.ai news.org":        "mw_ai_news",
}

# Language map — canonical lowercase tag → display label
_LANGUAGE_MAP: Dict[str, str] = {
    "telugu":      "telugu",
    "hindi":       "hindi",
    "tamil":       "tamil",
    "kannada":     "kannada",
    "malayalam":   "malayalam",
    "bengali":     "bengali",
    "marathi":     "marathi",
    "gujarati":    "gujarati",
    "punjabi":     "punjabi",
    "urdu":        "urdu",
    "odia":        "odia",
    "english":     "english",
    "spanish":     "spanish",
    "french":      "french",
    "german":      "german",
    "japanese":    "japanese",
    "chinese":     "chinese",
    "arabic":      "arabic",
    "portuguese":  "portuguese",
}

_INTENT_PATTERNS = [
    (r"\b(create|make|write|generate|build|produce|draft)\b",   "content_generation"),
    (r"\b(research|find|search|look up|investigate|explore)\b", "research"),
    (r"\b(plan|schedule|organise|organize|content plan)\b",     "planning"),
    (r"\b(morning|briefing|brief me|start my day)\b",           "briefing"),
]


# ── Helpers ─────────────────────────────────────────────────────────────────────

def _normalise_brand_url(text: str) -> str:
    """
    Turn URL-style brand fragments into matchable text.
    e.g.  "mw.ai edu.org"  →  "mw.ai edu.org"  (kept as-is, in _BRAND_MAP)
          "mw.ai"          →  "mw ai"
    """
    # Normalise dots between letters to spaces so "mw.ai" → "mw ai"
    return re.sub(r"(?<=[a-z])\.(?=[a-z])", " ", text, flags=re.IGNORECASE)


def _parse_quantity(text: str) -> int:
    number_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    m = re.search(r"\b(\d+)\b", text)
    if m:
        return min(int(m.group(1)), 10)
    low = text.lower()
    for word, val in number_words.items():
        if word in low:
            return val
    return 3


def _parse_formats(text: str) -> List[str]:
    found: List[str] = []
    low = text.lower()
    for kw in sorted(_FORMAT_MAP.keys(), key=len, reverse=True):
        if kw in low and _FORMAT_MAP[kw] not in found:
            found.append(_FORMAT_MAP[kw])
    return found or ["insight"]


def _parse_platforms(text: str) -> List[str]:
    found: List[str] = []
    low = text.lower()
    for kw, plat in _PLATFORM_MAP.items():
        if kw in low and plat not in found:
            found.append(plat)
    return found


def _parse_brand(text: str) -> str:
    low = _normalise_brand_url(text.lower())
    for kw in sorted(_BRAND_MAP.keys(), key=len, reverse=True):
        if kw in low:
            return _BRAND_MAP[kw]
    return "janani_ai"


def _parse_language(text: str) -> str:
    """
    Detect a language mention in the message.
    Returns canonical lowercase language tag, or "" if not found.

    Matches patterns like:
      "in telugu", "in hindi", "telugu version", "telugu content"
    """
    low = text.lower()
    # First try "in <language>" pattern
    m = re.search(
        r"\bin\s+(" + "|".join(re.escape(lang) for lang in _LANGUAGE_MAP) + r")\b",
        low,
    )
    if m:
        return _LANGUAGE_MAP[m.group(1)]
    # Then bare language word
    for lang in sorted(_LANGUAGE_MAP.keys(), key=len, reverse=True):
        if re.search(rf"\b{re.escape(lang)}\b", low):
            return _LANGUAGE_MAP[lang]
    return ""


def _parse_intent(text: str) -> str:
    low = text.lower()
    for pattern, intent in _INTENT_PATTERNS:
        if re.search(pattern, low):
            return intent
    return "content_generation"


def _extract_topic(text: str) -> str:
    """
    Strip verbs, counts, format words, brand names, platform names, language
    phrases, and URL-style brand fragments, leaving only the core topic.
    """
    cleaned = text

    # Normalise URL-style brand text first so stripping works
    cleaned = _normalise_brand_url(cleaned)

    # Strip leading intent verb
    cleaned = re.sub(
        r"^(create|make|write|generate|build|produce|draft|research|find|plan)\s+",
        "", cleaned, flags=re.IGNORECASE,
    ).strip()

    # Strip quantity words
    cleaned = re.sub(
        r"\b(a|an|\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        "", cleaned, flags=re.IGNORECASE,
    ).strip()

    # Strip multi-word format phrases first, then single-word
    for kw in sorted(_FORMAT_MAP.keys(), key=len, reverse=True):
        cleaned = re.sub(rf"\b{re.escape(kw)}\b", "", cleaned, flags=re.IGNORECASE)

    # Strip "in <language>" and bare language words
    lang_pattern = "|".join(re.escape(lang) for lang in _LANGUAGE_MAP)
    cleaned = re.sub(rf"\bin\s+({lang_pattern})\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(rf"\b({lang_pattern})\b", "", cleaned, flags=re.IGNORECASE)

    # Strip filler prepositions
    cleaned = re.sub(
        r"\b(about|on|for|regarding|related to|covering|on the topic of)\b",
        "", cleaned, flags=re.IGNORECASE,
    )

    # Strip brand names (longest first to avoid partial matches)
    for kw in sorted(_BRAND_MAP.keys(), key=len, reverse=True):
        cleaned = re.sub(rf"\b{re.escape(kw)}\b", "", cleaned, flags=re.IGNORECASE)

    # Strip platform names
    for kw in _PLATFORM_MAP:
        cleaned = re.sub(rf"\b{re.escape(kw)}\b", "", cleaned, flags=re.IGNORECASE)

    # Strip stray URL fragments (e.g. ".org", ".ai", "edu.org")
    cleaned = re.sub(r"\b\w+\.(org|ai|com|io|net|co)\b", "", cleaned, flags=re.IGNORECASE)

    topic = " ".join(cleaned.split()).strip(" ,.-_/")
    return topic if len(topic) > 2 else text.strip()


def _regex_parse(message: str) -> Dict:
    return {
        "intent":    _parse_intent(message),
        "topic":     _extract_topic(message),
        "formats":   _parse_formats(message),
        "brand":     _parse_brand(message),
        "quantity":  _parse_quantity(message),
        "platforms": _parse_platforms(message),
        "language":  _parse_language(message),
        "raw":       message,
    }


# ── Output validator / normaliser ───────────────────────────────────────────────

def _validate(raw_intent: Dict, original_message: str) -> Dict:
    """
    Normalise and clamp an intent dict so downstream code always receives
    clean, in-range values regardless of what the LLM returned.
    """
    intent = raw_intent.get("intent", "content_generation")
    if intent not in VALID_INTENTS:
        intent = "content_generation"

    brand = raw_intent.get("brand", "janani_ai")
    if brand not in VALID_BRANDS:
        brand = _parse_brand(brand + " " + original_message)

    formats = raw_intent.get("formats", [])
    if not isinstance(formats, list):
        formats = [str(formats)]
    formats = [f for f in formats if f in VALID_FORMATS]
    if not formats:
        formats = _parse_formats(original_message)

    platforms = raw_intent.get("platforms", [])
    if not isinstance(platforms, list):
        platforms = [str(platforms)]
    platforms = [p for p in platforms if p in VALID_PLATFORMS]

    topic = str(raw_intent.get("topic", "")).strip()
    if not topic:
        topic = _extract_topic(original_message)
    else:
        # Even LLM-returned topics may still contain brand/lang fragments
        topic = _extract_topic(topic + " " + original_message) if not topic else _clean_topic(topic, original_message)

    try:
        quantity = max(1, min(int(raw_intent.get("quantity", 3)), 10))
    except (TypeError, ValueError):
        quantity = _parse_quantity(original_message)

    # Language: prefer LLM value if present, else regex-detect from original message
    language = str(raw_intent.get("language", "")).strip().lower()
    if language not in _LANGUAGE_MAP:
        language = _parse_language(original_message)

    return {
        "intent":    intent,
        "topic":     topic,
        "formats":   formats,
        "brand":     brand,
        "quantity":  quantity,
        "platforms": platforms,
        "language":  language,
        "raw":       original_message,
    }


def _clean_topic(topic: str, original_message: str) -> str:
    """Strip brand/language fragments from an LLM-returned topic string."""
    cleaned = _normalise_brand_url(topic)
    # Strip brand
    for kw in sorted(_BRAND_MAP.keys(), key=len, reverse=True):
        cleaned = re.sub(rf"\b{re.escape(kw)}\b", "", cleaned, flags=re.IGNORECASE)
    # Strip language
    lang_pattern = "|".join(re.escape(lang) for lang in _LANGUAGE_MAP)
    cleaned = re.sub(rf"\bin\s+({lang_pattern})\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(rf"\b({lang_pattern})\b", "", cleaned, flags=re.IGNORECASE)
    # Strip URL fragments
    cleaned = re.sub(r"\b\w+\.(org|ai|com|io|net|co)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = " ".join(cleaned.split()).strip(" ,.-_/")
    # If we stripped too much, fall back to regex-extracting from the original
    return cleaned if len(cleaned) > 2 else _extract_topic(original_message)


# ── LLM-enhanced parser ─────────────────────────────────────────────────────────

_LLM_PROMPT_TEMPLATE = """\
You are JAN's intent parser. Extract structured intent from the user's message.

Brands available:
  - janani_ai          (founder personal brand, AI/startup content)
  - mw_ai_data_systems (data pipelines, MLOps, analytics)
  - mw_ai_news         (AI news headlines, research updates)
  - mw_ai_edu          (tutorials, how-to guides, learning content)
    Aliases: "mw edu", "mw.ai edu.org", "mw ai edu"

User message: "{message}"

Return ONLY a JSON object with these exact keys (no markdown fences, no explanation):
{{
  "intent":    "<content_generation|research|planning|briefing|unknown>",
  "topic":     "<the core subject only — no brand names, no language words>",
  "formats":   ["<one or more of: thread, insight, short_video, tutorial, long_form, case_study, short_explainer>"],
  "brand":     "<one of the four brands above, default janani_ai>",
  "quantity":  <integer 1-10, default 3>,
  "platforms": ["<zero or more of: twitter, linkedin, youtube, instagram>"],
  "language":  "<detected language like telugu/hindi/english, or empty string>"
}}

Extraction rules:
- "reel" or "short" → short_video
- "post" or "linkedin post" → insight
- "thread" or "tweet" → thread
- "guide" or "tutorial" → tutorial
- "mw edu" / "mw.ai edu.org" / "mw ai edu" → brand = mw_ai_edu
- "in telugu" / "in hindi" etc → language field, NOT part of topic
- topic must NOT include brand names, language names, or format words
- If morning briefing / start my day → intent = briefing
- If only research verb, no create verb → intent = research
- If no brand mentioned → default janani_ai
"""


def _llm_parse(message: str) -> Dict:
    """Use the LLM to extract intent. Falls back to regex if parsing fails."""
    prompt = _LLM_PROMPT_TEMPLATE.format(message=message.replace('"', "'"))
    raw = llm_brain.generate_text(prompt)

    # Strip markdown code fences
    clean = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    # Find first JSON object in the response
    json_match = re.search(r"\{.*\}", clean, re.DOTALL)
    if json_match:
        clean = json_match.group(0)

    try:
        parsed = json.loads(clean)
        logger.debug("LLM intent raw: %s", parsed)
        return _validate(parsed, message)
    except Exception as exc:
        logger.warning("LLM intent parse failed (%s) — using regex fallback", exc)
        return _regex_parse(message)


# ── Public API ──────────────────────────────────────────────────────────────────

def interpret_user_message(message: str, *, use_llm: bool = True) -> Dict:
    """
    Parse a natural language message into a structured workflow intent.

    Args:
        message : Free-text user command, e.g.
                  "create 5 reels on prompt engineering in telugu in mw.ai edu.org"
        use_llm : Try LLM first (default True). Falls back to regex if Ollama
                  is offline or the output cannot be parsed.

    Returns:
        Intent dict with keys: intent, topic, formats, brand, quantity,
        platforms, language, raw. Values are always normalised and in-range.
    """
    if not message or not message.strip():
        return {
            "intent": "unknown", "topic": "", "formats": [],
            "brand": "janani_ai", "quantity": 0, "platforms": [],
            "language": "", "raw": message,
        }

    result = _llm_parse(message) if use_llm else _regex_parse(message)

    logger.info(
        "Intent parsed: intent=%s topic='%s' formats=%s qty=%d brand=%s lang=%s",
        result["intent"], result["topic"], result["formats"],
        result["quantity"], result["brand"], result.get("language", ""),
    )
    return result


def format_intent(intent: Dict) -> str:
    """Pretty-print an intent dict for display in the CLI."""
    lines = [
        "\n  🎯 Intent Understood:",
        f"     Intent    : {intent.get('intent', '—')}",
        f"     Topic     : {intent.get('topic', '—')}",
        f"     Format(s) : {', '.join(intent.get('formats', [])) or '—'}",
        f"     Quantity  : {intent.get('quantity', 3)}",
        f"     Brand     : {intent.get('brand', '—')}",
    ]
    if intent.get("language"):
        lines.append(f"     Language  : {intent['language']}")
    if intent.get("platforms"):
        lines.append(f"     Platforms : {', '.join(intent['platforms'])}")
    return "\n".join(lines)


__all__ = ["interpret_user_message", "format_intent"]
