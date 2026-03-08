# -*- coding: utf-8 -*-
"""JAN Manager v4: Department-style multi-agent orchestration.

Departments:
  Morning Intake → Research → Strategy → Content Factory → Review → Publish → Analytics → Learn
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
        self._intake: Dict                 = {}
        self._plan: List[Dict]             = []
        self._drafts: List[Dict]           = []
        self._review: Dict                 = {}
        self._publish_results: List[Dict]  = []
        self._multiplication: List[Dict]   = []
        self._last_intent: Dict            = {}

    # ── 1. Morning Intake Department ───────────────────────────────────────────

    def intake(self, pdf_path: str = "") -> str:
        """Read founder's research PDFs + notes → structured goals."""
        from agents.morning_intake_agent import MorningIntakeAgent
        agent = MorningIntakeAgent(brand=self.brand)
        kwargs = {}
        if pdf_path:
            kwargs["pdf_path"] = pdf_path
        self._intake = agent.run(**kwargs)
        return agent.format_output(self._intake)

    # ── 1b. Idea Intelligence Engine ──────────────────────────────────────────

    def trends(self, query: str = "AI and technology") -> str:
        """Run full Idea Intelligence pipeline: Trends → Rank → Ideas."""
        lines = []
        # TrendAgent
        from agents.trend_agent import TrendAgent
        trend = TrendAgent(brand=self.brand)
        trend_data = trend.run(query=query)
        lines.append(trend.format_output(trend_data))

        # TopicRanker
        from agents.topic_ranker import TopicRanker
        ranker = TopicRanker(brand=self.brand)
        ranked = ranker.run(trends=trend_data.get("trends", []))
        lines.append(ranker.format_output(ranked))

        # IdeaGenerator
        from agents.idea_generator import IdeaGenerator
        generator = IdeaGenerator(brand=self.brand)
        ideas = generator.run(ranked_topics=ranked.get("ranked_topics", []), count=3)
        lines.append(generator.format_output(ideas))

        return "\n".join(lines)

    def ideas(self, topic: str) -> str:
        """Generate ideas for a specific topic."""
        from agents.idea_generator import IdeaGenerator
        generator = IdeaGenerator(brand=self.brand)
        result = generator.run(topic=topic)
        return generator.format_output(result)

    def decide(self, question: str) -> str:
        """Run multi-agent consensus on a decision."""
        from ai_core.consensus_engine import ConsensusEngine
        engine = ConsensusEngine(brand=self.brand)
        result = engine.decide(
            question=question,
            agents=["trend", "strategy", "analytics"],
        )
        return engine.format_output(result)

    # ── 2. Research Department ─────────────────────────────────────────────────

    def research(self, topic: str) -> str:
        self._research_results = research_agent.run(topic, brand=self.brand)
        return research_agent.format_output(self._research_results)

    # ── 3. Strategy Department ─────────────────────────────────────────────────

    def plan_today(self) -> str:
        if not self._research_results:
            self._research_results = research_agent.run("", brand=self.brand)
        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes or None,
        )
        return planner_agent.format_output(self._plan)

    # ── 4. Content Factory ─────────────────────────────────────────────────────

    def generate_drafts(self) -> str:
        if not self._plan:
            return "⚠️  No plan found. Run 'plan today' first."
        self._drafts = content_agent.run(self._plan)
        return content_agent.format_output(self._drafts)

    def write_linkedin(self, topic: str) -> str:
        """Generate a LinkedIn post using the LinkedIn Writer Agent."""
        from agents.writers.linkedin_writer import LinkedInWriter
        writer = LinkedInWriter(brand=self.brand)
        result = writer.run(topic=topic)
        self._drafts = result.get("drafts", [])
        return writer.format_output(result)

    def write_twitter(self, topic: str) -> str:
        """Generate a Twitter thread using the Twitter Writer Agent."""
        from agents.writers.twitter_writer import TwitterWriter
        writer = TwitterWriter(brand=self.brand)
        result = writer.run(topic=topic)
        self._drafts = result.get("drafts", [])
        return writer.format_output(result)

    def write_instagram(self, topic: str) -> str:
        from agents.writers.instagram_writer import InstagramWriter
        writer = InstagramWriter(brand=self.brand)
        result = writer.run(topic=topic)
        self._drafts = result.get("drafts", [])
        return writer.format_output(result)

    def write_youtube(self, topic: str) -> str:
        from agents.writers.youtube_writer import YouTubeWriter
        writer = YouTubeWriter(brand=self.brand)
        result = writer.run(topic=topic)
        self._drafts = result.get("drafts", [])
        return writer.format_output(result)

    def write_newsletter(self, topic: str) -> str:
        from agents.writers.newsletter_writer import NewsletterWriter
        writer = NewsletterWriter(brand=self.brand)
        result = writer.run(topic=topic)
        self._drafts = result.get("drafts", [])
        return writer.format_output(result)

    # ── 5. Quality Control Department ──────────────────────────────────────────

    def review_drafts(self) -> str:
        """Run drafts through the QC Review Agent before approval."""
        if not self._drafts:
            return "⚠️  No drafts to review. Generate content first."
        from agents.review_agent import ReviewAgent
        reviewer = ReviewAgent(brand=self.brand)
        self._review = reviewer.run(drafts=self._drafts)
        # Replace drafts with only passed ones
        self._drafts = self._review.get("passed", [])
        return reviewer.format_output(self._review)

    # ── 6. Publishing Department ───────────────────────────────────────────────

    def publish_drafts(self, *, dry_run: bool = True) -> str:
        if not self._drafts:
            return "⚠️  No drafts found. Run 'generate drafts' first."

        # Store in vector memory before publishing
        try:
            from memory_engine.vector_store import posts_store
            vs = posts_store()
            for i, d in enumerate(self._drafts):
                doc_id = f"draft_{d.get('topic', 'x')[:30]}_{i}"
                vs.add(doc_id, d.get("draft", ""), {
                    "platform": d.get("platform", ""),
                    "brand": d.get("brand", self.brand),
                })
        except Exception:
            pass

        self._publish_results = publisher_agent.run(self._drafts, dry_run=True)
        return publisher_agent.format_output(self._publish_results)

    # ── 7. Content Multiplication ──────────────────────────────────────────────

    def multiply(self, topic: str) -> str:
        from content_engine.multiplier import multiply_quick, format_multiplication_report
        idea = {"title": topic, "summary": f"Create multi-platform content about: {topic}"}
        self._multiplication = multiply_quick(idea, brand=self.brand)

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
        lines = [report, f"\n✅  {len(self._multiplication)} drafts added to approval queue."]
        for i, asset in enumerate(self._multiplication[:3], 1):
            preview = asset.get("draft", "")[:120]
            lines.append(f"\n  📄 {asset['content_type']} ({asset['platform']}):")
            lines.append(f"     {preview}...")
        if len(self._multiplication) > 3:
            lines.append(f"\n  ... and {len(self._multiplication) - 3} more assets")
        return "\n".join(lines)

    # ── Morning Briefing (full pipeline) ───────────────────────────────────────

    def morning_briefing(self) -> str:
        lines = []

        # Intake
        lines.append(self.intake())

        # Morning notes
        self._morning_notes = morning_reader.read_morning_notes()
        lines.append(morning_reader.format_briefing(self._morning_notes))

        # Research
        focus = (self._intake.get("intake", {}).get("topics", []) or
                 self._morning_notes.get("focus_topics", []))
        seed = focus[0] if focus else ""
        self._research_results = research_agent.run(seed, brand=self.brand)
        lines.append(research_agent.format_output(self._research_results))

        # Learning cycle
        try:
            from ai_core.performance_learner import learn
            learning = learn()
            if learning.get("events_analyzed", 0) > 0:
                lines.append(f"\n🧠 Learning: analyzed {learning['events_analyzed']} events.")
        except Exception:
            pass

        # Plan
        self._plan = planner_agent.run(
            self._research_results,
            brand=self.brand,
            morning_notes=self._morning_notes,
        )
        lines.append(planner_agent.format_output(self._plan))

        # LLM info
        try:
            from ai_core.llm_router import get_active_provider
            lines.append(f"\n  🤖 LLM: {get_active_provider()}")
        except Exception:
            pass

        lines.append("\n✅  Briefing complete. Try: 'write linkedin <topic>' or 'multiply <topic>'")
        return "\n".join(lines)

    # ── Topic Insights ─────────────────────────────────────────────────────────

    def topic_insights(self) -> str:
        top    = topic_memory.top_performers(self.brand, limit=5)
        recent = topic_memory.recent_topics(self.brand, limit=5)
        reco   = topic_memory.recommended_topics(self.brand, limit=5)
        lines = [f"\n🧠 Topic Intelligence — Brand: {self.brand}"]
        if not top and not recent:
            lines.append("  No history yet.")
            return "\n".join(lines)
        if top:
            lines.append("\n  🏆 Top Performing:")
            for r in top:
                lines.append(f"     • {r['topic'][:55]} | score: {r.get('performance_score', 0):.2f}")
        if reco:
            lines.append("\n  💡 Recommended:")
            for r in reco:
                lines.append(f"     • {r['topic'][:55]}")
        return "\n".join(lines)

    # ── Workflow Execution (NL gateway) ────────────────────────────────────────

    def execute_workflow(self, message: str) -> str:
        sections = []

        # Controller Agent
        try:
            from agents.controller_agent import ControllerAgent
            controller = ControllerAgent(brand=self.brand)
            analysis = controller.run(message=message, brand=self.brand)
            sections.append(controller.format_output(analysis))
            intent_name = analysis.get("intent", "create")
            params = analysis.get("params", {})
            topic = params.get("topic", "")

            if intent_name == "multiply":
                sections.append(self.multiply(topic or message))
                return "\n".join(sections)
        except Exception:
            analysis = None

        # Fallback workflow
        intent = workflow_interpreter.interpret_user_message(message)
        self._last_intent = intent
        if analysis is None:
            sections.append(workflow_interpreter.format_intent(intent))

        if intent["intent"] == "unknown":
            sections.append(
                "\n⚠️  Could not understand. Try:\n"
                "   write linkedin <topic> | write twitter <topic>\n"
                "   multiply <topic> | research <topic> | morning briefing"
            )
            return "\n".join(sections)

        if intent["intent"] == "briefing":
            return "\n".join(sections) + "\n\n" + self.morning_briefing()

        topic    = intent.get("topic", "")
        quantity = intent.get("quantity", 3)
        formats  = intent.get("formats", ["insight"])
        language = intent.get("language", "")

        # Step 1: Research
        sections.append("\n" + "─" * 55 + "\n  📡 Researching...")
        self._research_results = research_agent.run(topic or "", brand=self.brand)
        sections.append(research_agent.format_output(self._research_results))

        if intent["intent"] == "research":
            return "\n".join(sections)

        # Step 2: Plan
        sections.append("\n" + "─" * 55 + "\n  🧠 Building strategy...")
        workflow_notes = {
            "focus_topics":  [topic] if topic else [],
            "content_goals": [f"{quantity} × {f}" for f in formats],
            "tasks": [], "notes": [f"User: {message}"],
        }
        self._plan = planner_agent.run(
            self._research_results, brand=self.brand,
            morning_notes=workflow_notes, quantity=quantity,
            formats=formats, language=language,
        )
        sections.append(planner_agent.format_output(self._plan))

        if intent["intent"] == "planning":
            return "\n".join(sections)

        # Step 3: Generate + Review
        sections.append("\n" + "─" * 55 + "\n  ✍️  Writing with Gemini...")
        self._drafts = content_agent.run(self._plan)
        sections.append(content_agent.format_output(self._drafts))

        # Auto-review
        sections.append("\n" + "─" * 55 + "\n  🔍 Quality review...")
        sections.append(self.review_drafts())

        sections.append(
            "\n✅  Pipeline complete!"
            "\n   'publish drafts' to simulate | 'multiply <topic>' for all platforms"
        )
        return "\n".join(sections)

    # ── Status ─────────────────────────────────────────────────────────────────

    def status(self) -> str:
        mem_count = len(topic_memory.all_records(self.brand))
        try:
            from ai_core.llm_router import get_active_provider
            llm_info = get_active_provider()
        except Exception:
            llm_info = "ollama"

        # Cost info
        try:
            from ai_core.cost_controller import get_controller
            cc = get_controller()
            usage = cc.usage_dict()
            cost_line = (
                f"  API Usage      : {usage['daily_calls']}/{usage['max_calls']} calls, "
                f"{usage['daily_tokens']:,}/{usage['max_tokens']:,} tokens"
            )
        except Exception:
            cost_line = "  API Usage      : tracking disabled"

        # Vector memory
        try:
            from memory_engine.vector_store import posts_store
            vec_count = posts_store().count()
            vec_line = f"  Vector memory  : {vec_count} posts stored"
        except Exception:
            vec_line = "  Vector memory  : not initialized"

        lines = [
            f"\n📊 JAN Department Status — Brand: {self.brand}",
            f"  LLM Provider   : {llm_info}",
            cost_line,
            f"  Intake          : {'✅' if self._intake else '—'}",
            f"  Research items  : {len(self._research_results)}",
            f"  Plan tasks      : {len(self._plan)}",
            f"  Drafts          : {len(self._drafts)}",
            f"  Review          : {self._review.get('pass_rate', '—')}",
            f"  Published       : {len(self._publish_results)}",
            f"  Multiplied      : {len(self._multiplication)}",
            f"  Topic memory    : {mem_count} records",
            vec_line,
        ]
        return "\n".join(lines)
