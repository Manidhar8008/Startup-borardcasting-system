# -*- coding: utf-8 -*-
"""Morning Intake Agent — Reads founder's daily research and extracts structured goals.

Reads PDFs and text files from brain_input/research/, uses Gemini to extract
ideas, topics, goals, and research insights. Outputs a structured DailyIntake
for downstream agents.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register

logger = logging.getLogger("agent.intake")

EXTRACTION_PROMPT = """You are JAN, an AI content strategist for brand '{brand}'.

Analyze the following founder research notes and extract:

1. IDEAS: Creative content ideas mentioned or implied (list 3-8)
2. TOPICS: Key topics/themes to cover (list 3-6)
3. GOALS: Explicit or implied goals for today (list 2-4)
4. INSIGHTS: Research insights worth sharing with an audience (list 2-5)
5. PRIORITY: The single most important theme to focus on today

Format your response EXACTLY as:
IDEAS:
- <idea 1>
- <idea 2>

TOPICS:
- <topic 1>
- <topic 2>

GOALS:
- <goal 1>
- <goal 2>

INSIGHTS:
- <insight 1>
- <insight 2>

PRIORITY: <one line summary>

Research Notes:
\"\"\"
{content}
\"\"\"

Output only the structured extraction. No preamble."""


def _parse_extraction(raw: str) -> Dict:
    """Parse the LLM extraction into structured sections."""
    sections: Dict[str, List[str]] = {
        "ideas": [], "topics": [], "goals": [], "insights": [],
    }
    priority = ""
    current_key = None

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        upper = line.upper()
        if upper.startswith("IDEAS"):
            current_key = "ideas"
        elif upper.startswith("TOPICS"):
            current_key = "topics"
        elif upper.startswith("GOALS"):
            current_key = "goals"
        elif upper.startswith("INSIGHTS"):
            current_key = "insights"
        elif upper.startswith("PRIORITY:"):
            priority = line.split(":", 1)[1].strip()
            current_key = None
        elif line.startswith("- ") and current_key:
            sections[current_key].append(line[2:].strip())
        elif current_key and line and not line.endswith(":"):
            sections[current_key].append(line)

    return {
        "ideas": sections["ideas"],
        "topics": sections["topics"],
        "goals": sections["goals"],
        "insights": sections["insights"],
        "priority": priority,
    }


@register
class MorningIntakeAgent(BaseAgent):
    name = "intake"
    role = "morning_intake"
    description = (
        "Reads founder's daily PDF research files, extracts ideas, topics, "
        "goals, and insights using Gemini. Produces structured daily intake."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Process morning intake from PDFs and text files.

        Expected kwargs:
            pdf_path (str, optional): Specific PDF to process.
            text (str, optional): Direct text input.

        Returns:
            Dict with 'intake' (structured goals), 'sources', 'timestamp'.
        """
        content_parts = []
        sources = []

        # 1. Read specific PDF if provided
        pdf_path = kwargs.get("pdf_path")
        if pdf_path:
            from brain_input.pdf_reader import read_pdf
            text = read_pdf(pdf_path)
            if text:
                content_parts.append(text)
                sources.append(f"pdf:{pdf_path}")

        # 2. Read latest PDF from research directory
        if not content_parts:
            try:
                from brain_input.pdf_reader import latest_pdf
                latest = latest_pdf()
                if latest and latest.get("text"):
                    content_parts.append(latest["text"])
                    sources.append(f"pdf:{latest['filename']}")
            except Exception:
                pass

        # 3. Read text files via brain_parser
        try:
            from brain_input.brain_parser import parse_all
            parsed = parse_all()
            for item in parsed:
                title = item.get("title", "")
                summary = item.get("summary", "")
                if title or summary:
                    content_parts.append(f"{title}: {summary}")
                    sources.append(f"notes:{item.get('source', 'brain')}")
        except Exception:
            pass

        # 4. Read morning notes
        try:
            from brain_input.morning_reader import read_morning_notes
            notes = read_morning_notes()
            if notes.get("focus_topics"):
                content_parts.append("Focus topics: " + ", ".join(notes["focus_topics"]))
                sources.append("morning_notes")
            if notes.get("tasks"):
                content_parts.append("Tasks: " + ", ".join(notes["tasks"]))
            if notes.get("notes"):
                content_parts.append("Notes: " + " ".join(notes["notes"]))
        except Exception:
            pass

        # 5. Accept direct text
        direct_text = kwargs.get("text", "")
        if direct_text:
            content_parts.append(direct_text)
            sources.append("direct_input")

        if not content_parts:
            return {
                "intake": {"ideas": [], "topics": [], "goals": [], "insights": [], "priority": ""},
                "sources": [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "empty",
                "error": "No research files found. Add PDFs to brain_input/research/ or write morning_notes.md",
            }

        # 6. Use Gemini to extract structured goals
        combined = "\n\n---\n\n".join(content_parts)
        # Truncate to avoid token limits
        if len(combined) > 15000:
            combined = combined[:15000] + "\n\n[truncated]"

        prompt = EXTRACTION_PROMPT.format(brand=self.brand, content=combined)

        try:
            from ai_core.llm_router import generate
            raw = generate(prompt=prompt, temperature=0.4, max_tokens=1500)
            intake = _parse_extraction(raw)
        except Exception as exc:
            logger.warning("LLM extraction failed: %s", exc)
            # Fallback: use content as-is
            intake = {
                "ideas": [p[:100] for p in content_parts[:5]],
                "topics": [],
                "goals": [],
                "insights": [],
                "priority": content_parts[0][:100] if content_parts else "",
            }

        return {
            "intake": intake,
            "sources": sources,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "processed",
            "content_chars": len(combined),
        }

    def format_output(self, data: Any) -> str:
        intake = data.get("intake", {})
        sources = data.get("sources", [])

        lines = ["\n☀️  Morning Intake Report"]
        lines.append(f"  Sources: {', '.join(sources) if sources else 'none'}")

        if data.get("error"):
            lines.append(f"\n  ⚠️  {data['error']}")
            return "\n".join(lines)

        if intake.get("priority"):
            lines.append(f"\n  🎯 Priority: {intake['priority']}")

        if intake.get("ideas"):
            lines.append("\n  💡 Ideas:")
            for idea in intake["ideas"][:6]:
                lines.append(f"     • {idea}")

        if intake.get("topics"):
            lines.append("\n  📌 Topics:")
            for topic in intake["topics"][:5]:
                lines.append(f"     • {topic}")

        if intake.get("goals"):
            lines.append("\n  🎯 Goals:")
            for goal in intake["goals"][:4]:
                lines.append(f"     • {goal}")

        if intake.get("insights"):
            lines.append("\n  🔬 Research Insights:")
            for insight in intake["insights"][:4]:
                lines.append(f"     • {insight}")

        return "\n".join(lines)
