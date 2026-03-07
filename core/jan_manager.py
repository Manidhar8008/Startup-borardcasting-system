"""JAN Manager: orchestrates all agents and maintains session state."""

import logging
from typing import Dict, List

from agents import research_agent, planner_agent, content_agent, publisher_agent
from brain_input import morning_reader
from memory import topic_memory

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

    # ── Commands ──────────────────────────────────────────────────────────────

    def research(self, topic: str) -> str:
        """Run the research agent on a given topic."""
        self._research_results = research_agent.run(topic, brand=self.brand)
        return research_agent.format_output(self._research_results)

    def plan_today(self) -> str:
        """Build today's LLM + intelligence-scored content plan."""
        if not self._research_results:
            self._research_results = research_agent.run("", brand=self.brand)

        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes or None,
        )
        return planner_agent.format_output(self._plan)

    def generate_drafts(self) -> str:
        """Generate LLM-powered content drafts."""
        if not self._plan:
            return "⚠️  No plan found. Run 'plan today' first."
        self._drafts = content_agent.run(self._plan)
        return content_agent.format_output(self._drafts)

    def publish_drafts(self, *, dry_run: bool = True) -> str:
        """Simulate publishing drafts and record topic usage in memory."""
        if not self._drafts:
            return "⚠️  No drafts found. Run 'generate drafts' first."
        self._publish_results = publisher_agent.run(self._drafts, dry_run=True)
        return publisher_agent.format_output(self._publish_results)

    def morning_briefing(self) -> str:
        """
        Full morning pipeline:
          1. Read morning notes
          2. Research focus topics
          3. Score + rank topics with Topic Intelligence
          4. Build LLM content plan
        """
        lines = []

        # Step 1 — Notes
        self._morning_notes = morning_reader.read_morning_notes()
        lines.append(morning_reader.format_briefing(self._morning_notes))

        # Step 2 — Research
        focus = self._morning_notes.get("focus_topics", [])
        seed  = focus[0] if focus else ""
        self._research_results = research_agent.run(seed, brand=self.brand)
        lines.append(research_agent.format_output(self._research_results))

        # Step 3+4 — Scored plan
        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes,
        )
        lines.append(planner_agent.format_output(self._plan))

        lines.append(
            "\n✅  Briefing complete. Type 'generate drafts' to write content."
        )
        return "\n".join(lines)

    def topic_insights(self) -> str:
        """Display Topic Intelligence insights: top performers, recent, recommended."""
        brand = self.brand

        top    = topic_memory.top_performers(brand, limit=5)
        recent = topic_memory.recent_topics(brand, limit=5)
        reco   = topic_memory.recommended_topics(brand, limit=5)

        lines = [f"\n🧠 Topic Intelligence Insights — Brand: {brand}"]

        if not top and not recent:
            lines.append(
                "\n  No topic history yet. Run 'publish drafts' to start building memory."
            )
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
            lines.append("\n  💡 Recommended (high-perf, not used recently):")
            for r in reco:
                lines.append(f"     • {r['topic'][:55]}")

        return "\n".join(lines)

    def status(self) -> str:
        """Show current pipeline state."""
        mem_count = len(topic_memory.all_records(self.brand))
        lines = [
            f"\n📊 JAN Pipeline Status — Brand: {self.brand}",
            f"  Morning notes  : {'✅ loaded' if self._morning_notes else '—'}",
            f"  Research items : {len(self._research_results)}",
            f"  Plan tasks     : {len(self._plan)}",
            f"  Drafts         : {len(self._drafts)}",
            f"  Published      : {len(self._publish_results)}",
            f"  Topic memory   : {mem_count} records",
        ]
        return "\n".join(lines)
