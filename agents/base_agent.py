# -*- coding: utf-8 -*-
"""Base Agent — Abstract base class for all agents in the Manidhar Intelligence System.

Every agent must inherit from BaseAgent and implement:
  - run(**kwargs)        → execute the agent's core logic
  - format_output(data)  → human-readable string from run() output
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    """Abstract base class for all intelligence agents."""

    name: str = "base"
    role: str = "undefined"
    description: str = ""
    tools: List[str] = []          # MCP tool names this agent can access

    def __init__(self, brand: str = "janani_ai"):
        self.brand = brand
        self.logger = logging.getLogger(f"agent.{self.name}")

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the agent's primary task. Returns structured data."""
        ...

    @abstractmethod
    def format_output(self, data: Any) -> str:
        """Format the agent's output for human display."""
        ...

    def describe(self) -> Dict[str, Any]:
        """Return a machine-readable description of this agent."""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "tools": self.tools,
            "brand": self.brand,
        }

    def __repr__(self) -> str:
        return f"<Agent:{self.name} role='{self.role}' brand='{self.brand}'>"
