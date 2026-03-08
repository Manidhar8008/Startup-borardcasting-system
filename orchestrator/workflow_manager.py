# -*- coding: utf-8 -*-
"""Workflow Manager — Defines and executes named agent pipelines.

A workflow is a named sequence of steps. Each step is routed to an agent
via AgentRouter. The output of each agent becomes the input to the next.

Usage:
    wm = WorkflowManager(brand="janani_ai")
    result = wm.execute("full", initial_input={"topic": "AI agents"})
"""

import logging
import time
from typing import Any, Dict, List, Optional

from orchestrator.agent_router import AgentRouter

logger = logging.getLogger("orchestrator")


# ── Pipeline definitions ─────────────────────────────────────────────────────
# Each pipeline is an ordered list of step names that the AgentRouter resolves.

PIPELINES: Dict[str, List[str]] = {
    "full": [
        "research",
        "strategy",
        "content",
        "publish",
        "analytics",
    ],
    "research_only": [
        "research",
    ],
    "plan_only": [
        "research",
        "strategy",
    ],
    "create_content": [
        "research",
        "strategy",
        "content",
    ],
    "publish_flow": [
        "publish",
        "analytics",
    ],
}


class WorkflowManager:
    """Orchestrates agent pipelines by executing steps in sequence."""

    def __init__(self, brand: str = "janani_ai"):
        self.brand = brand
        self.router = AgentRouter(brand=brand)
        self._execution_log: List[Dict[str, Any]] = []

    def list_workflows(self) -> Dict[str, List[str]]:
        """Return all available workflow definitions."""
        return dict(PIPELINES)

    def get_workflow(self, name: str) -> List[str]:
        """Get step list for a named workflow."""
        if name not in PIPELINES:
            available = ", ".join(sorted(PIPELINES.keys()))
            raise KeyError(f"Workflow '{name}' not found. Available: {available}")
        return list(PIPELINES[name])

    def execute(
        self,
        workflow_name: str,
        *,
        initial_input: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a complete workflow pipeline.

        Args:
            workflow_name: Name of the pipeline to run (e.g. 'full').
            initial_input: Starting data passed to the first agent.

        Returns:
            Dict with 'outputs' (per-step results), 'log', and 'status'.
        """
        steps = self.get_workflow(workflow_name)
        invalid = self.router.validate_pipeline(steps)
        if invalid:
            return {
                "status": "error",
                "error": f"Pipeline has unregistered steps: {invalid}",
            }

        logger.info(
            "Starting workflow '%s' (%d steps) for brand '%s'",
            workflow_name, len(steps), self.brand,
        )

        data = initial_input or {}
        outputs: Dict[str, Any] = {}
        log_entries: List[Dict[str, Any]] = []

        for step in steps:
            start = time.time()
            try:
                agent = self.router.route(step)
                result = agent.run(**data)
                elapsed = round(time.time() - start, 2)

                outputs[step] = result
                log_entry = {
                    "step": step,
                    "agent": agent.name,
                    "status": "success",
                    "elapsed_s": elapsed,
                }
                log_entries.append(log_entry)
                logger.info(
                    "Step '%s' completed in %.2fs", step, elapsed,
                )

                # Pass this step's output forward as input to the next step.
                # Agents should return dicts; if they don't, wrap it.
                if isinstance(result, dict):
                    data.update(result)
                elif isinstance(result, list):
                    data[f"{step}_results"] = result

            except Exception as exc:
                elapsed = round(time.time() - start, 2)
                logger.error("Step '%s' failed: %s", step, exc)
                log_entries.append({
                    "step": step,
                    "status": "error",
                    "error": str(exc),
                    "elapsed_s": elapsed,
                })
                # Stop pipeline on failure
                self._execution_log = log_entries
                return {
                    "status": "error",
                    "failed_step": step,
                    "error": str(exc),
                    "outputs": outputs,
                    "log": log_entries,
                }

        self._execution_log = log_entries
        return {
            "status": "success",
            "workflow": workflow_name,
            "steps_completed": len(steps),
            "outputs": outputs,
            "log": log_entries,
        }

    def last_log(self) -> List[Dict[str, Any]]:
        """Return the execution log from the last run."""
        return list(self._execution_log)

    def format_log(self) -> str:
        """Format the last execution log for display."""
        if not self._execution_log:
            return "No workflow executed yet."
        lines = ["📋 Workflow Execution Log:"]
        for entry in self._execution_log:
            icon = "✅" if entry["status"] == "success" else "❌"
            lines.append(
                f"  {icon} {entry['step']:<12} → {entry.get('agent', '?'):<12} "
                f"({entry['elapsed_s']}s)"
            )
        return "\n".join(lines)
