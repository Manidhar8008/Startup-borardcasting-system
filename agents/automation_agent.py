# -*- coding: utf-8 -*-
"""Automation Agent — Executes tasks through a background scheduling loop.

Wraps tool calls, executes scheduled workflows (Morning Intake -> Research -> Plan -> Draft),
and manages the background automation engine state.
"""

import logging
import time
import threading
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from core.jan_manager import JanManager

logger = logging.getLogger("agent.automation")

@register
class AutomationAgent(BaseAgent):
    name = "automation"
    role = "automator"
    description = (
        "Background automation engine. Triggers scheduled workflows and publishing loops."
    )
    tools = []
    
    _instance = None
    _engine_thread = None
    _engine_running = False
    _last_run = None
    _next_run = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AutomationAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self, brand: str = "janani_ai"):
        if not hasattr(self, "_initialized"):
            super().__init__(brand=brand)
            self.manager = JanManager(brand=self.brand)
            self.check_interval_seconds = 60 * 60  # Default check every hour
            AutomationAgent._initialized = True

    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute automation actions.
        Expected kwargs: action (str) -> "start", "stop", "status"
        """
        action = kwargs.get("action", "status")

        if action == "start":
            return self.start_engine()
        elif action == "stop":
            return self.stop_engine()
        else:
            return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "is_running": AutomationAgent._engine_running,
            "last_run": AutomationAgent._last_run,
            "next_run": AutomationAgent._next_run,
        }

    def start_engine(self) -> Dict[str, Any]:
        if AutomationAgent._engine_running:
            return {"status": "success", "message": "Engine is already running."}
            
        AutomationAgent._engine_running = True
        AutomationAgent._engine_thread = threading.Thread(
            target=self._background_loop,
            daemon=True,
            name="AutomationEngineLoop"
        )
        AutomationAgent._engine_thread.start()
        logger.info("Automation engine started.")
        return {"status": "success", "message": "Automation engine started."}

    def stop_engine(self) -> Dict[str, Any]:
        if not AutomationAgent._engine_running:
            return {"status": "success", "message": "Engine is already stopped."}
            
        AutomationAgent._engine_running = False
        logger.info("Automation engine stopped.")
        return {"status": "success", "message": "Automation engine stopped."}

    def _background_loop(self):
        """The core background observe-think-act loop."""
        while AutomationAgent._engine_running:
            try:
                # Observe
                import datetime
                now = datetime.datetime.now()
                
                # Simple condition for MVP: run full pipeline at 8:00 AM once a day
                # For demo purposes, we will trigger it if _last_run is None
                # or if a full day has passed. 
                
                trigger = False
                if AutomationAgent._last_run is None:
                    trigger = True
                else:
                    last_time = datetime.datetime.fromisoformat(AutomationAgent._last_run)
                    if (now - last_time).total_seconds() > 86400: # 24 hours
                        trigger = True
                        
                # Think & Act
                if trigger:
                    logger.info("Automation loop triggered. Starting daily workflow...")
                    self._execute_daily_pipeline()
                    AutomationAgent._last_run = now.isoformat()
                    
                AutomationAgent._next_run = (now + datetime.timedelta(seconds=self.check_interval_seconds)).isoformat()
                
                # Sleep in small chunks to allow quick cancellation
                for _ in range(self.check_interval_seconds):
                    if not AutomationAgent._engine_running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Automation loop error: {str(e)}")
                time.sleep(60) # Backoff on error
    
    def _execute_daily_pipeline(self):
        """Executes the morning intake -> trends -> idea -> plan -> draft -> review -> queue."""
        logger.info("Automation: Running trends and ideas...")
        self.manager.trends()
        
        logger.info("Automation: Planning today...")
        self.manager.plan_today()
        
        logger.info("Automation: Generating drafts...")
        self.manager.generate_drafts()
        
        logger.info("Automation: Reviewing drafts...")
        self.manager.review_drafts()
        
        # At this point, passed drafts are automatically added to the ActionQueue or ApprovalQueue
        # depending on where review_drafts leaves them. Wait, currently review_drafts returns "passed"
        # but the JanManager needs to queue them. Let's do that:
        passed = self.manager._drafts
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(self.brand)
        for draft in passed:
            queue.add_draft(draft)
            
        logger.info(f"Automation: Pipeline complete. {len(passed)} drafts added to queue.")

    def format_output(self, data: Any) -> str:
        if isinstance(data, dict):
            status = "🟢 RUNNING" if data.get("is_running") else "🛑 STOPPED"
            return f"🤖 Automation Engine: {status}\nLast Run: {data.get('last_run')}\nNext Run:{data.get('next_run')}"
        return str(data)
