# -*- coding: utf-8 -*-
"""Base Agent v2 — Abstract base with Observe → Think → Act → Evaluate loop.

Every agent must inherit from BaseAgent and implement:
  - run(**kwargs)        → execute the agent's core logic (simple mode)
  - format_output(data)  → human-readable string from run() output

Agents that want the reasoning loop should also implement:
  - observe(context)     → gather information
  - think(observations)  → reason about what to do
  - act(plan)            → execute the plan
  - evaluate(result)     → check if definition_of_done is met

The loop repeats until evaluate() returns True or max_iterations is reached.
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
    max_iterations: int = 3        # Max reasoning loop iterations

    def __init__(self, brand: str = "janani_ai"):
        self.brand = brand
        self.logger = logging.getLogger(f"agent.{self.name}")
        self._iteration_count = 0
        self._reasoning_log: List[Dict] = []

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute the agent's primary task. Returns structured data."""
        ...

    @abstractmethod
    def format_output(self, data: Any) -> str:
        """Format the agent's output for human display."""
        ...

    # ── Reasoning Loop Methods (override to enable) ──────────────────────────

    def observe(self, context: Dict) -> Dict:
        """Gather information from available sources.

        Override this to implement observation logic.
        Default: passes context through unchanged.
        """
        return context

    def think(self, observations: Dict) -> Dict:
        """Reason about the observations and form a plan.

        Override this to implement reasoning logic.
        Default: returns observations as the plan.
        """
        return observations

    def act(self, plan: Dict) -> Dict:
        """Execute the plan and produce a result.

        Override this to implement action logic.
        Default: calls run(**plan) for backward compatibility.
        """
        return self.run(**plan)

    def evaluate(self, result: Any) -> bool:
        """Check if the definition of done is met.

        Override this to implement evaluation logic.
        Default: returns True (single iteration).
        """
        return True

    def definition_of_done(self) -> str:
        """Describe what 'done' means for this agent.

        Override to provide agent-specific completion criteria.
        """
        return "Task completed in a single pass."

    # ── Reasoning Loop Execution ─────────────────────────────────────────────

    def run_loop(self, context: Optional[Dict] = None, **kwargs) -> Dict:
        """Execute the Observe → Think → Act → Evaluate loop.

        Args:
            context: Initial context dict.
            **kwargs: Additional parameters.

        Returns:
            Dict with 'result', 'iterations', 'reasoning_log', 'converged'.
        """
        context = context or kwargs or {}
        self._iteration_count = 0
        self._reasoning_log = []
        result = None

        # Check cost controller
        try:
            from ai_core.cost_controller import get_controller
            cc = get_controller()
        except ImportError:
            cc = None

        while self._iteration_count < self.max_iterations:
            self._iteration_count += 1
            iteration_entry = {"iteration": self._iteration_count}

            # Cost control check
            if cc:
                try:
                    cc.record_loop()
                    cc.check()
                except Exception as exc:
                    self.logger.warning("Cost limit in loop: %s", exc)
                    iteration_entry["stopped"] = "cost_limit"
                    self._reasoning_log.append(iteration_entry)
                    break

            try:
                # 1. Observe
                observations = self.observe(context)
                iteration_entry["observed"] = bool(observations)

                # 2. Think
                plan = self.think(observations)
                iteration_entry["planned"] = bool(plan)

                # 3. Act
                result = self.act(plan)
                iteration_entry["acted"] = True

                # 4. Evaluate
                done = self.evaluate(result)
                iteration_entry["done"] = done
                self._reasoning_log.append(iteration_entry)

                if done:
                    self.logger.info(
                        "Agent '%s' converged after %d iteration(s)",
                        self.name, self._iteration_count,
                    )
                    break

                # Feed result back as context for next iteration
                if isinstance(result, dict):
                    context.update(result)

            except Exception as exc:
                self.logger.error("Reasoning loop error at iteration %d: %s", self._iteration_count, exc)
                iteration_entry["error"] = str(exc)
                self._reasoning_log.append(iteration_entry)
                break

        return {
            "result": result,
            "iterations": self._iteration_count,
            "reasoning_log": self._reasoning_log,
            "converged": self._iteration_count < self.max_iterations,
        }

    # ── Metadata ─────────────────────────────────────────────────────────────

    def describe(self) -> Dict[str, Any]:
        """Return a machine-readable description of this agent."""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "tools": self.tools,
            "brand": self.brand,
            "max_iterations": self.max_iterations,
            "definition_of_done": self.definition_of_done(),
        }

    def __repr__(self) -> str:
        return f"<Agent:{self.name} role='{self.role}' brand='{self.brand}'>"
