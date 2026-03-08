# -*- coding: utf-8 -*-
"""JAN Manager: orchestrates all agents and maintains session state."""

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
        self._last_intent: Dict            = {}

    # ── Individual commands ────────────────────────────────────────────────────

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

    def morning_briefing(self) -> str:
        lines = []
        self._morning_notes = morning_reader.read_morning_notes()
        lines.append(morning_reader.format_briefing(self._morning_notes))

        focus = self._morning_notes.get("focus_topics", [])
        seed  = focus[0] if focus else ""
        self._research_results = research_agent.run(seed, brand=self.brand)
        lines.append(research_agent.format_output(self._research_results))

        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes,
        )
        lines.append(planner_agent.format_output(self._plan))
        lines.append("\n✅  Briefing complete. Type 'generate drafts' to write content.")
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

    # ── Workflow execution ─────────────────────────────────────────────────────

    def execute_workflow(self, message: str) -> str:
        """
        Full natural-language pipeline:
            parse intent → [research] → [score+plan] → [draft generation]

        Intent routing:
          content_generation  → research + score + plan + drafts  (full pipeline)
          research            → research only
          planning            → research + score + plan (no drafts)
          briefing            → delegates to morning_briefing()
          unknown             → helpful error message

        Args:
            message: Free-text user command, e.g.
                     "create 3 reels about AI agents for janani_ai"

        Returns:
            Multi-section formatted string with all pipeline output.
        """
        sections = []

        # ── Step 0: Parse intent with LLM (regex fallback when offline) ──────
        intent = workflow_interpreter.interpret_user_message(message)
        self._last_intent = intent
        sections.append(workflow_interpreter.format_intent(intent))

        if intent["intent"] == "unknown":
            sections.append(
                "\n\n⚠️  Could not understand your request.\n"
                "   Try:  do create 3 threads about AI agents\n"
                "         do research prompt engineering\n"
                "         do plan today\n"
                "         morning briefing"
            )
            return "\n".join(sections)

        # Delegate briefing entirely
        if intent["intent"] == "briefing":
            return "\n".join(sections) + "\n\n" + self.morning_briefing()

        # Honour brand switch requested in the message
        if intent.get("brand") and intent["brand"] != self.brand:
            self.brand = intent["brand"]
            sections.append(f"\n  🔀 Brand switched to: {self.brand}")

        topic    = intent.get("topic", "")
        quantity = intent.get("quantity", 3)
        formats  = intent.get("formats", ["insight"])
        language = intent.get("language", "")

        # ── Step 1: Research ──────────────────────────────────────────────────
        sections.append("\n" + "─" * 55)
        sections.append("  📡 Step 1 — Researching...")
        self._research_results = research_agent.run(topic or "", brand=self.brand)
        sections.append(research_agent.format_output(self._research_results))

        # research intent stops here
        if intent["intent"] == "research":
            sections.append(
                "\n✅  Research complete!"
                "\n   Type 'plan today' to build a scored content plan from these results."
            )
            return "\n".join(sections)

        # ── Step 2: Score topics + build LLM plan ────────────────────────────
        sections.append("\n" + "─" * 55)
        sections.append("  🧠 Step 2 — Scoring topics + building LLM plan...")

        # Surface format/quantity preferences to the planner via workflow_notes
        workflow_notes = {
            "focus_topics":  [topic] if topic else [],
            "content_goals": [f"{quantity} \u00d7 {f}" for f in formats],
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

        # planning intent stops here (no drafts)
        if intent["intent"] == "planning":
            sections.append(
                "\n✅  Planning complete!"
                "\n   Type 'generate drafts' to write content for this plan."
            )
            return "\n".join(sections)

        # ── Step 3: Generate drafts (content_generation intent) ───────────────
        sections.append("\n" + "─" * 55)
        sections.append("  \u270d\ufe0f  Step 3 — Writing drafts with LLM...")
        self._drafts = content_agent.run(self._plan)
        sections.append(content_agent.format_output(self._drafts))

        sections.append(
            "\n\n\u2705  Workflow complete!"
            "\n   Type 'publish drafts' when you're ready to simulate publishing."
        )
        return "\n".join(sections)

    # ── Status ─────────────────────────────────────────────────────────────────

    def status(self) -> str:
        mem_count  = len(topic_memory.all_records(self.brand))
        intent_str = (
            f"'{self._last_intent.get('raw', '')}'"
            if self._last_intent else "—"
        )
        lines = [
            f"\n📊 JAN Pipeline Status — Brand: {self.brand}",
            f"  Last workflow  : {intent_str}",
            f"  Morning notes  : {'✅ loaded' if self._morning_notes else '—'}",
            f"  Research items : {len(self._research_results)}",
            f"  Plan tasks     : {len(self._plan)}",
            f"  Drafts         : {len(self._drafts)}",
            f"  Published      : {len(self._publish_results)}",
            f"  Topic memory   : {mem_count} records",
        ]
        return "\n".join(lines)
