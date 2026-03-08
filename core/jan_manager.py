# -*- coding: utf-8 -*-
"""JAN Manager v3: orchestrates all agents via the WorkflowManager.

Upgrades:
  - Gemini-powered via LLM router
  - Orchestrator-driven pipelines
  - Content multiplication (1 idea → N assets)
  - Performance learning feedback loop
  - Backward-compatible individual commands
"""

import logging
from typing import Dict, List

from agents import research_agent, planner_agent, content_agent, publisher_agent
from brain_input import morning_reader
from memory import topic_memory
from ai_core import workflow_interpreter

logger = logging.getLogger("engine")


class JanManager:
    DEFAULT_BRAND = "janani_ai"

    def __init__(self, brand: str = DEFAULT_BRAND):
        self.brand = brand
        self._research_results: List[Dict] = []
        self._morning_notes: Dict          = {}
        self._plan: List[Dict]             = []
        self._drafts: List[Dict]           = []
        self._publish_results: List[Dict]  = []
        self._multiplication: List[Dict]   = []
        self._last_intent: Dict            = {}

    # ── Orchestrator access ────────────────────────────────────────────────────

    def _get_workflow_manager(self):
        from orchestrator.workflow_manager import WorkflowManager
        return WorkflowManager(brand=self.brand)

    # ── Individual commands (backward-compatible) ──────────────────────────────

    def research(self, topic: str) -> str:
        self._research_results = research_agent.run(topic, brand=self.brand)
        return research_agent.format_output(self._research_results)

    def plan_today(self) -> str:
        if not self._research_results:
            self._research_results = research_agent.run("", brand=self.brand)
        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes or None,
        )
        return planner_agent.format_output(self._plan)

    def generate_drafts(self) -> str:
        if not self._plan:
            return "⚠️  No plan found. Run 'plan today' first."
        self._drafts = content_agent.run(self._plan)
        return content_agent.format_output(self._drafts)

    def publish_drafts(self, *, dry_run: bool = True) -> str:
        if not self._drafts:
            return "⚠️  No drafts found. Run 'generate drafts' first."
        self._publish_results = publisher_agent.run(self._drafts, dry_run=True)
        return publisher_agent.format_output(self._publish_results)

    # ── New: Content Multiplication ────────────────────────────────────────────

    def multiply(self, topic: str) -> str:
        """Multiply 1 idea into content for all platforms via Gemini."""
        from content_engine.multiplier import multiply_quick, format_multiplication_report

        idea = {"title": topic, "summary": f"Create multi-platform content about: {topic}"}
        self._multiplication = multiply_quick(idea, brand=self.brand)

        # Send all multiplied assets to the approval queue
        from decision_engine.approval_queue import ApprovalQueue
        queue = ApprovalQueue(self.brand)
        for asset in self._multiplication:
            queue.add_draft({
                "topic": asset.get("idea_source", topic),
                "draft": asset.get("draft", ""),
                "platform": asset.get("platform", ""),
                "content_type": asset.get("content_type", ""),
                "brand": self.brand,
            })

        report = format_multiplication_report(self._multiplication)
        lines = [report]
        lines.append(f"\n✅  {len(self._multiplication)} drafts added to approval queue.")
        lines.append("   Type 'publish drafts' to simulate publishing.")

        # Show preview of first 3 assets
        for i, asset in enumerate(self._multiplication[:3], 1):
            draft_preview = asset.get("draft", "")[:120]
            lines.append(f"\n  📄 {asset['content_type']} ({asset['platform']}):")
            lines.append(f"     {draft_preview}...")

        if len(self._multiplication) > 3:
            lines.append(f"\n  ... and {len(self._multiplication) - 3} more assets")

        return "\n".join(lines)

    # ── New: Morning Briefing v2 ───────────────────────────────────────────────

    def morning_briefing(self) -> str:
        lines = []
        self._morning_notes = morning_reader.read_morning_notes()
        lines.append(morning_reader.format_briefing(self._morning_notes))

        focus = self._morning_notes.get("focus_topics", [])
        seed  = focus[0] if focus else ""
        self._research_results = research_agent.run(seed, brand=self.brand)
        lines.append(research_agent.format_output(self._research_results))

        # Run learning cycle to update patterns
        try:
            from ai_core.performance_learner import learn
            learning = learn()
            if learning.get("events_analyzed", 0) > 0:
                lines.append(f"\n🧠 Learning: analyzed {learning['events_analyzed']} events, "
                             f"{len(learning.get('topic_boosts', {}))} topic patterns learned.")
        except Exception:
            pass

        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes,
        )
        lines.append(planner_agent.format_output(self._plan))

        # Show LLM provider
        try:
            from ai_core.llm_router import get_active_provider
            lines.append(f"\n  🤖 LLM: {get_active_provider()}")
        except Exception:
            pass

        lines.append("\n✅  Briefing complete. Type 'generate drafts' or 'multiply <topic>' next.")
        return "\n".join(lines)

    def topic_insights(self) -> str:
        brand  = self.brand
        top    = topic_memory.top_performers(brand, limit=5)
        recent = topic_memory.recent_topics(brand, limit=5)
        reco   = topic_memory.recommended_topics(brand, limit=5)

        lines = [f"\n🧠 Topic Intelligence Insights — Brand: {brand}"]
        if not top and not recent:
            lines.append("\n  No history yet. Run 'publish drafts' to build memory.")
            return "\n".join(lines)

        if top:
            lines.append("\n  🏆 Top Performing Topics:")
            for r in top:
                lines.append(
                    f"     • {r['topic'][:55]}"
                    f" | score: {r.get('performance_score', 0):.2f}"
                    f" | used: {r.get('times_used', 0)}x"
                )
        if recent:
            lines.append("\n  🕐 Recently Used Topics:")
            for r in recent:
                lines.append(
                    f"     • {r['topic'][:55]}"
                    f" | last: {r.get('last_used', '')[:10]}"
                )
        if reco:
            lines.append("\n  💡 Recommended (high-perf, fresh):")
            for r in reco:
                lines.append(f"     • {r['topic'][:55]}")

        return "\n".join(lines)

    # ── Workflow execution (upgraded with controller agent) ─────────────────────

    def execute_workflow(self, message: str) -> str:
        sections = []

        # Step 0: Use Controller Agent to parse intent
        try:
            from agents.controller_agent import ControllerAgent
            controller = ControllerAgent(brand=self.brand)
            analysis = controller.run(message=message, brand=self.brand)
            sections.append(controller.format_output(analysis))

            intent_name = analysis.get("intent", "create")
            params = analysis.get("params", {})
            topic = params.get("topic", "")

            # Handle multiply intent
            if intent_name == "multiply":
                sections.append("\n" + "─" * 55)
                sections.append("  🔄 Multiplication Mode Activated")
                sections.append(self.multiply(topic or message))
                return "\n".join(sections)

        except Exception:
            # Fallback to old workflow interpreter
            analysis = None

        # Fall back to existing workflow logic
        intent = workflow_interpreter.interpret_user_message(message)
        self._last_intent = intent
        if analysis is None:
            sections.append(workflow_interpreter.format_intent(intent))

        if intent["intent"] == "unknown":
            sections.append(
                "\n\n⚠️  Could not understand your request.\n"
                "   Try:  create 3 threads about AI agents\n"
                "         multiply AI agents\n"
                "         research prompt engineering\n"
                "         morning briefing"
            )
            return "\n".join(sections)

        if intent["intent"] == "briefing":
            return "\n".join(sections) + "\n\n" + self.morning_briefing()

        if intent.get("brand") and intent["brand"] != self.brand:
            self.brand = intent["brand"]
            sections.append(f"\n  🔀 Brand switched to: {self.brand}")

        topic    = intent.get("topic", "")
        quantity = intent.get("quantity", 3)
        formats  = intent.get("formats", ["insight"])
        language = intent.get("language", "")

        # Step 1: Research
        sections.append("\n" + "─" * 55)
        sections.append("  📡 Step 1 — Researching...")
        self._research_results = research_agent.run(topic or "", brand=self.brand)
        sections.append(research_agent.format_output(self._research_results))

        if intent["intent"] == "research":
            sections.append(
                "\n✅  Research complete!"
                "\n   Type 'plan today' to build a scored content plan."
            )
            return "\n".join(sections)

        # Step 2: Score + Plan
        sections.append("\n" + "─" * 55)
        sections.append("  🧠 Step 2 — Scoring topics + building LLM plan...")

        workflow_notes = {
            "focus_topics":  [topic] if topic else [],
            "content_goals": [f"{quantity} × {f}" for f in formats],
            "tasks":         [],
            "notes":         [f"User requested: {message}"],
        }

        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=workflow_notes,
            quantity=quantity,
            formats=formats,
            language=language,
        )
        sections.append(planner_agent.format_output(self._plan))

        if intent["intent"] == "planning":
            sections.append(
                "\n✅  Planning complete!"
                "\n   Type 'generate drafts' to write content."
            )
            return "\n".join(sections)

        # Step 3: Generate drafts (via Gemini)
        sections.append("\n" + "─" * 55)
        sections.append("  ✍️  Step 3 — Writing drafts with Gemini...")
        self._drafts = content_agent.run(self._plan)
        sections.append(content_agent.format_output(self._drafts))

        sections.append(
            "\n\n✅  Workflow complete!"
            "\n   Type 'publish drafts' to simulate publishing."
            "\n   Type 'multiply <topic>' to create content for all 9 platforms."
        )
        return "\n".join(sections)

    # ── Status ─────────────────────────────────────────────────────────────────

    def status(self) -> str:
        mem_count  = len(topic_memory.all_records(self.brand))
        intent_str = (
            f"'{self._last_intent.get('raw', '')}'"
            if self._last_intent else "—"
        )

        # Get LLM provider
        try:
            from ai_core.llm_router import get_active_provider
            llm_info = get_active_provider()
        except Exception:
            llm_info = "ollama"

        lines = [
            f"\n📊 JAN Pipeline Status — Brand: {self.brand}",
            f"  LLM Provider   : {llm_info}",
            f"  Last workflow   : {intent_str}",
            f"  Morning notes   : {'✅ loaded' if self._morning_notes else '—'}",
            f"  Research items  : {len(self._research_results)}",
            f"  Plan tasks      : {len(self._plan)}",
            f"  Drafts          : {len(self._drafts)}",
            f"  Published       : {len(self._publish_results)}",
            f"  Multiplied      : {len(self._multiplication)}",
            f"  Topic memory    : {mem_count} records",
        ]
        return "\n".join(lines)
