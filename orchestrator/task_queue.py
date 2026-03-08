# -*- coding: utf-8 -*-
"""Task Queue — In-memory queue for deferred pipeline execution.

Holds pending workflow tasks that can be executed later.
Designed for future async/background processing expansion.

Usage:
    tq = TaskQueue()
    task_id = tq.enqueue("full", brand="janani_ai", input_data={"topic": "AI"})
    task = tq.dequeue()  # returns the oldest pending task
    tq.mark_done(task_id, result={...})
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("orchestrator")


class TaskQueue:
    """Simple in-memory FIFO queue for workflow tasks."""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._order: List[str] = []  # insertion order for FIFO

    def enqueue(
        self,
        workflow_name: str,
        *,
        brand: str = "janani_ai",
        input_data: Optional[Dict[str, Any]] = None,
        priority: int = 0,
    ) -> str:
        """Add a workflow task to the queue.

        Returns:
            task_id: Unique identifier for the queued task.
        """
        task_id = str(uuid.uuid4())[:8]
        task = {
            "id": task_id,
            "workflow": workflow_name,
            "brand": brand,
            "input": input_data or {},
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "result": None,
        }
        self._tasks[task_id] = task
        self._order.append(task_id)
        logger.info("Enqueued task %s: workflow='%s' brand='%s'", task_id, workflow_name, brand)
        return task_id

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Pop the oldest pending task from the queue."""
        for task_id in self._order:
            task = self._tasks.get(task_id)
            if task and task["status"] == "pending":
                task["status"] = "running"
                return task
        return None

    def mark_done(self, task_id: str, result: Any = None) -> None:
        """Mark a task as completed with its result."""
        task = self._tasks.get(task_id)
        if task:
            task["status"] = "done"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            task["result"] = result

    def mark_failed(self, task_id: str, error: str) -> None:
        """Mark a task as failed."""
        task = self._tasks.get(task_id)
        if task:
            task["status"] = "failed"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            task["result"] = {"error": error}

    def pending_count(self) -> int:
        """Count of pending tasks."""
        return sum(1 for t in self._tasks.values() if t["status"] == "pending")

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtering by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)
