# -*- coding: utf-8 -*-
"""Controller Agent — Master orchestrator that interprets requests and drives pipelines.

The controller is the "brain" agent: it takes natural language input,
determines which workflow to execute, selects prompt difficulty,
and reports results.
"""

from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.agent_registry import register


@register
class ControllerAgent(BaseAgent):
    name = "controller"
    role = "orchestrator"
    description = (
        "Master agent that interprets natural language requests, "
        "selects the right workflow, manages prompt difficulty, "
        "and coordinates all other agents."
    )
    tools = []

    # Keyword → workflow mapping for intent detection
    _INTENT_MAP = {
        "multiply": "multiply",
        "create": "create_content",
        "write": "create_content",
        "make": "create_content",
        "generate": "create_content",
        "research": "research_only",
        "plan": "plan_only",
        "publish": "publish_flow",
        "full": "full",
        "automate": "full",
    }

    # Content complexity → prompt difficulty
    _COMPLEXITY_MAP = {
        "thread": "easy",
        "tweet": "easy",
        "caption": "easy",
        "facebook_post": "easy",
        "insight": "medium",
        "linkedin_post": "medium",
        "newsletter": "medium",
        "blog": "medium",
        "youtube_script": "hard",
        "tutorial": "hard",
        "case_study": "hard",
        "podcast": "hard",
        "youtube_short": "medium",
    }

    def run(self, **kwargs) -> Dict[str, Any]:
        """Interpret a request and determine execution plan.

        Expected kwargs:
            message (str): Natural language input from the user.
            brand (str): Target brand override.

        Returns:
            Dict with 'intent', 'workflow', 'params', 'difficulty'.
        """
        message = kwargs.get("message", "")
        brand = kwargs.get("brand", self.brand)

        intent = self._detect_intent(message)
        params = self._extract_params(message, brand)
        difficulty = self._select_difficulty(params.get("content_type", "insight"))

        return {
            "intent": intent,
            "workflow": self._INTENT_MAP.get(intent, "create_content"),
            "params": params,
            "difficulty": difficulty,
            "brand": brand,
            "original_message": message,
        }

    def _detect_intent(self, message: str) -> str:
        """Detect the primary intent from a natural language message."""
        lower = message.lower()
        for keyword, intent in self._INTENT_MAP.items():
            if keyword in lower:
                return keyword
        return "create"

    def _extract_params(self, message: str, brand: str) -> Dict:
        """Extract structured parameters from a natural language message."""
        lower = message.lower()

        # Detect content type
        content_type = "insight"
        for ct in ["thread", "tutorial", "case_study", "blog", "newsletter",
                    "podcast", "youtube_short", "youtube_script", "caption",
                    "reel", "linkedin", "tweet", "facebook"]:
            if ct in lower:
                content_type = ct
                break

        # Detect quantity
        quantity = 1
        import re
        qty_match = re.search(r"(\d+)\s+(post|thread|reel|caption|draft|article|piece)", lower)
        if qty_match:
            quantity = min(int(qty_match.group(1)), 20)

        # Detect topic (everything after "about" or "on")
        topic = ""
        for sep in ["about ", "on ", "regarding ", "for "]:
            if sep in lower:
                topic = message[lower.index(sep) + len(sep):].strip().rstrip(".")
                break
        if not topic:
            topic = message

        return {
            "topic": topic,
            "content_type": content_type,
            "quantity": quantity,
            "brand": brand,
        }

    def _select_difficulty(self, content_type: str) -> str:
        """Select prompt difficulty based on content complexity."""
        return self._COMPLEXITY_MAP.get(content_type, "medium")

    def format_output(self, data: Any) -> str:
        lines = [
            f"\n🧠 Controller Analysis:",
            f"  Intent    : {data.get('intent', '?')}",
            f"  Workflow  : {data.get('workflow', '?')}",
            f"  Difficulty: {data.get('difficulty', 'medium')}",
            f"  Topic     : {data.get('params', {}).get('topic', '?')}",
            f"  Type      : {data.get('params', {}).get('content_type', '?')}",
            f"  Quantity  : {data.get('params', {}).get('quantity', 1)}",
            f"  Brand     : {data.get('brand', '?')}",
        ]
        return "\n".join(lines)
