# -*- coding: utf-8 -*-
"""Agent Registry — Central registry for discovering and instantiating agents.

Usage:
    from agents.agent_registry import register, get_agent, list_agents

    @register
    class MyAgent(BaseAgent): ...

    agent = get_agent("my_agent", brand="janani_ai")
"""

from typing import Dict, List, Optional, Type

from agents.base_agent import BaseAgent

# Global registry: agent_name → agent_class
_REGISTRY: Dict[str, Type[BaseAgent]] = {}


def register(cls: Type[BaseAgent]) -> Type[BaseAgent]:
    """Class decorator that registers an agent by its `name` attribute."""
    if not hasattr(cls, "name") or not cls.name:
        raise ValueError(f"Agent class {cls.__name__} must define a 'name' attribute.")
    _REGISTRY[cls.name] = cls
    return cls


def get_agent(name: str, brand: str = "janani_ai") -> BaseAgent:
    """Instantiate a registered agent by name."""
    cls = _REGISTRY.get(name)
    if cls is None:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise KeyError(f"Agent '{name}' not found. Available: {available}")
    return cls(brand=brand)


def get_agent_class(name: str) -> Optional[Type[BaseAgent]]:
    """Return the agent class without instantiating."""
    return _REGISTRY.get(name)


def list_agents() -> List[Dict[str, str]]:
    """List all registered agents with their metadata."""
    return [
        {"name": cls.name, "role": cls.role, "description": cls.description}
        for cls in _REGISTRY.values()
    ]


def registered_names() -> List[str]:
    """Return sorted list of registered agent names."""
    return sorted(_REGISTRY.keys())
