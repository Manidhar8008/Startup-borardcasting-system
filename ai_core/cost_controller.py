# -*- coding: utf-8 -*-
"""Cost Controller — Prevents runaway API usage.

Tracks LLM calls, tokens, and loop iterations per session and per day.
The LLM router checks this before every call.

Usage:
    from ai_core.cost_controller import CostController
    cc = CostController()
    cc.check()           # Raises CostLimitExceeded if over limit
    cc.record_call(tokens=500)
    print(cc.usage_report())
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

logger = logging.getLogger("cost")

USAGE_FILE = Path(__file__).resolve().parent.parent / "memory_engine" / "daily_usage.json"

# Default limits (overridable via .env)
DEFAULT_MAX_LLM_CALLS = 100
DEFAULT_MAX_TOKENS = 500_000
DEFAULT_MAX_LOOPS = 20


class CostLimitExceeded(Exception):
    """Raised when an API usage limit is exceeded."""
    pass


class CostController:
    """Tracks and enforces API usage limits."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.max_calls = int(os.getenv("MAX_LLM_CALLS_PER_DAY", DEFAULT_MAX_LLM_CALLS))
        self.max_tokens = int(os.getenv("MAX_TOKENS_PER_DAY", DEFAULT_MAX_TOKENS))
        self.max_loops = int(os.getenv("MAX_LOOP_ITERATIONS", DEFAULT_MAX_LOOPS))

        self._session_calls = 0
        self._session_tokens = 0
        self._session_loops = 0

        self._load_daily()

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _load_daily(self):
        """Load or reset daily usage counters."""
        if USAGE_FILE.exists():
            try:
                data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
                if data.get("date") == self._today():
                    self._daily_calls = data.get("calls", 0)
                    self._daily_tokens = data.get("tokens", 0)
                    return
            except Exception:
                pass
        self._daily_calls = 0
        self._daily_tokens = 0

    def _save_daily(self):
        """Persist daily usage."""
        USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "date": self._today(),
            "calls": self._daily_calls,
            "tokens": self._daily_tokens,
        }
        USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def check(self):
        """Check if any limit is exceeded. Raises CostLimitExceeded."""
        if self._daily_calls >= self.max_calls:
            raise CostLimitExceeded(
                f"Daily LLM call limit reached ({self._daily_calls}/{self.max_calls}). "
                "Set MAX_LLM_CALLS_PER_DAY in .env to increase."
            )
        if self._daily_tokens >= self.max_tokens:
            raise CostLimitExceeded(
                f"Daily token limit reached ({self._daily_tokens:,}/{self.max_tokens:,}). "
                "Set MAX_TOKENS_PER_DAY in .env to increase."
            )
        if self._session_loops >= self.max_loops:
            raise CostLimitExceeded(
                f"Loop iteration limit reached ({self._session_loops}/{self.max_loops}). "
                "Set MAX_LOOP_ITERATIONS in .env to increase."
            )

    def record_call(self, tokens: int = 0):
        """Record an LLM API call."""
        self._session_calls += 1
        self._session_tokens += tokens
        self._daily_calls += 1
        self._daily_tokens += tokens
        self._save_daily()

    def record_loop(self):
        """Record a loop iteration (for agent loops)."""
        self._session_loops += 1

    def reset_session(self):
        """Reset session counters (not daily)."""
        self._session_calls = 0
        self._session_tokens = 0
        self._session_loops = 0

    def usage_report(self) -> str:
        """Generate a human-readable usage report."""
        return (
            f"\n💰 Cost Control Report:\n"
            f"  Session : {self._session_calls} calls, {self._session_tokens:,} tokens\n"
            f"  Today   : {self._daily_calls}/{self.max_calls} calls, "
            f"{self._daily_tokens:,}/{self.max_tokens:,} tokens\n"
            f"  Loops   : {self._session_loops}/{self.max_loops}"
        )

    def usage_dict(self) -> Dict:
        """Return usage data as dict."""
        return {
            "session_calls": self._session_calls,
            "session_tokens": self._session_tokens,
            "daily_calls": self._daily_calls,
            "daily_tokens": self._daily_tokens,
            "max_calls": self.max_calls,
            "max_tokens": self.max_tokens,
            "remaining_calls": max(0, self.max_calls - self._daily_calls),
            "remaining_tokens": max(0, self.max_tokens - self._daily_tokens),
        }

    @property
    def is_within_limits(self) -> bool:
        """Quick check without raising."""
        return (
            self._daily_calls < self.max_calls
            and self._daily_tokens < self.max_tokens
            and self._session_loops < self.max_loops
        )


# Module-level convenience
_controller = None

def get_controller() -> CostController:
    global _controller
    if _controller is None:
        _controller = CostController()
    return _controller
