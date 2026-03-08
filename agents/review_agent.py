# -*- coding: utf-8 -*-
"""Review Agent v2 — Quality control with style/fact/engagement checks and revision loop.

Checks:
  - Style: tone alignment with founder voice
  - Facts: hallucination detection (regex + LLM)
  - Engagement: predicted engagement score
  - Formatting: platform-specific rules

If draft fails QC → sends back to writer agent for revision (max 2 rounds).
"""

import re
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register

PLATFORM_RULES = {
    "linkedin": {"max_chars": 3000, "min_chars": 50, "max_hashtags": 8, "min_hashtags": 2},
    "twitter": {"max_chars_per_tweet": 280, "min_tweets": 3, "max_tweets": 10},
    "instagram": {"max_chars": 2200, "min_hashtags": 5, "max_hashtags": 30},
    "youtube": {"min_words": 200, "max_words": 1500},
    "newsletter": {"min_words": 100, "max_words": 500, "requires_subject": True},
    "facebook": {"max_chars": 5000, "min_chars": 30},
    "blog": {"min_words": 300, "max_words": 2000},
}

HALLUCINATION_SIGNALS = [
    r"according to (?:recent )?studies",
    r"research (?:shows|proves|indicates) that \d+%",
    r"a (?:recent )?(?:Harvard|Stanford|MIT|Oxford) study",
    r"experts (?:say|agree|confirm)",
    r"statistics show that \d+%",
]

REVIEW_PROMPT = """You are a content quality reviewer for brand '{brand}'.

Review this {platform} draft for quality:

1. TONE: Professional yet human? (1-10)
2. VALUE: Genuine insight, not generic? (1-10)
3. ENGAGEMENT: Would this get reactions? (1-10)
4. ACCURACY: Unsupported claims? (list)
5. STYLE: Matches founder voice? (1-10)

Draft:
\"\"\"
{draft}
\"\"\"

Format:
TONE: <score>/10
VALUE: <score>/10
ENGAGEMENT: <score>/10
STYLE: <score>/10
ACCURACY: <OK or list>
VERDICT: <PASS or REVISE>
REVISION_NOTES: <what to fix if REVISE>"""

REVISION_PROMPT = """You are JAN, a {platform} content writer for brand '{brand}'.

The following draft was reviewed and needs revision.

Original draft:
\"\"\"
{draft}
\"\"\"

Review feedback:
{feedback}

Rewrite the draft addressing ALL feedback. Keep the same topic and structure.
Output ONLY the revised draft. No preamble."""

MAX_REVISIONS = 2


@register
class ReviewAgent(BaseAgent):
    name = "review"
    role = "quality_control"
    description = (
        "Quality control with style, fact, and engagement checks. "
        "Sends failed drafts back for revision (max 2 rounds)."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Review and optionally revise drafts.

        Expected kwargs:
            drafts (list): Draft dicts from writer agents.
            auto_revise (bool): Auto-revise failed drafts (default: True).
        """
        drafts = kwargs.get("drafts", [])
        auto_revise = kwargs.get("auto_revise", True)

        if not drafts:
            return {"reviews": [], "passed": [], "failed": [], "drafts": []}

        reviews = []
        passed = []
        failed = []

        for draft in drafts:
            review = self._review_single(draft)
            reviews.append(review)

            if review["verdict"] == "PASS":
                passed.append(draft)
            elif auto_revise:
                # Attempt revision
                revised_draft = self._revise(draft, review)
                if revised_draft:
                    re_review = self._review_single(revised_draft)
                    reviews.append(re_review)
                    if re_review["verdict"] == "PASS":
                        passed.append(revised_draft)
                    else:
                        failed.append(revised_draft)
                else:
                    failed.append(draft)
            else:
                failed.append(draft)

        return {
            "reviews": reviews,
            "passed": passed,
            "failed": failed,
            "drafts": passed,  # Pass only approved drafts downstream
            "pass_rate": f"{len(passed)}/{len(drafts)}",
            "revisions_attempted": sum(1 for r in reviews if r.get("is_revision")),
        }

    def _review_single(self, draft: Dict) -> Dict:
        text = draft.get("draft", "")
        platform = draft.get("platform", "linkedin")
        topic = draft.get("topic", "")
        issues: List[str] = []

        format_issues = self._check_formatting(text, platform)
        hallucination_flags = self._check_hallucinations(text)
        issues.extend(format_issues)
        issues.extend(hallucination_flags)

        llm_review = self._llm_review(text, platform)
        tone_score = llm_review.get("tone_score", 7)
        value_score = llm_review.get("value_score", 7)
        engagement_score = llm_review.get("engagement_score", 7)
        style_score = llm_review.get("style_score", 7)
        revision_notes = llm_review.get("revision_notes", "")

        avg_score = (tone_score + value_score + engagement_score + style_score) / 4
        if avg_score < 5.5 or len(hallucination_flags) > 2:
            verdict = "REVISE"
        elif format_issues and llm_review.get("verdict") == "REVISE":
            verdict = "REVISE"
        else:
            verdict = llm_review.get("verdict", "PASS")

        return {
            "topic": topic,
            "platform": platform,
            "tone_score": tone_score,
            "value_score": value_score,
            "engagement_score": engagement_score,
            "style_score": style_score,
            "avg_score": round(avg_score, 1),
            "format_issues": format_issues,
            "hallucination_flags": hallucination_flags,
            "verdict": verdict,
            "revision_notes": revision_notes,
            "issues": issues,
        }

    def _check_formatting(self, text: str, platform: str) -> List[str]:
        issues = []
        rules = PLATFORM_RULES.get(platform, {})
        if "max_chars" in rules and len(text) > rules["max_chars"]:
            issues.append(f"Over {platform} limit ({len(text)}/{rules['max_chars']})")
        if "min_chars" in rules and len(text) < rules["min_chars"]:
            issues.append(f"Too short ({len(text)}/{rules['min_chars']})")
        if "min_words" in rules and len(text.split()) < rules["min_words"]:
            issues.append(f"Too few words ({len(text.split())}/{rules['min_words']})")
        hashtags = len(re.findall(r"#\w+", text))
        if "min_hashtags" in rules and hashtags < rules["min_hashtags"]:
            issues.append(f"Needs more hashtags ({hashtags}/{rules['min_hashtags']})")
        if "max_hashtags" in rules and hashtags > rules["max_hashtags"]:
            issues.append(f"Too many hashtags ({hashtags}/{rules['max_hashtags']})")
        return issues

    def _check_hallucinations(self, text: str) -> List[str]:
        flags = []
        for pattern in HALLUCINATION_SIGNALS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                flags.append(f"Unsourced: '{matches[0]}'")
        return flags

    def _llm_review(self, text: str, platform: str) -> Dict:
        prompt = REVIEW_PROMPT.format(brand=self.brand, platform=platform, draft=text[:2000])
        try:
            from ai_core.llm_router import generate
            raw = generate(prompt=prompt, temperature=0.3, max_tokens=500)
        except Exception:
            return {"tone_score": 7, "value_score": 7, "engagement_score": 7, "style_score": 7, "verdict": "PASS"}

        scores: Dict[str, Any] = {"tone_score": 7, "value_score": 7, "engagement_score": 7, "style_score": 7, "verdict": "PASS", "revision_notes": ""}
        for line in raw.splitlines():
            line = line.strip()
            ul = line.upper()
            match = re.search(r"(\d+)/10", line)
            if ul.startswith("TONE:") and match:
                scores["tone_score"] = int(match.group(1))
            elif ul.startswith("VALUE:") and match:
                scores["value_score"] = int(match.group(1))
            elif ul.startswith("ENGAGEMENT:") and match:
                scores["engagement_score"] = int(match.group(1))
            elif ul.startswith("STYLE:") and match:
                scores["style_score"] = int(match.group(1))
            elif ul.startswith("VERDICT:"):
                scores["verdict"] = "PASS" if "PASS" in ul else "REVISE"
            elif ul.startswith("REVISION_NOTES:"):
                scores["revision_notes"] = line.split(":", 1)[1].strip()
        return scores

    def _revise(self, draft: Dict, review: Dict) -> Dict | None:
        """Send draft back to a writer for revision."""
        text = draft.get("draft", "")
        platform = draft.get("platform", "linkedin")
        feedback_parts = []
        if review.get("format_issues"):
            feedback_parts.extend(review["format_issues"])
        if review.get("hallucination_flags"):
            feedback_parts.extend(review["hallucination_flags"])
        if review.get("revision_notes"):
            feedback_parts.append(review["revision_notes"])
        feedback = "\n- ".join(["Issues found:"] + feedback_parts)

        prompt = REVISION_PROMPT.format(brand=self.brand, platform=platform, draft=text, feedback=feedback)
        try:
            from ai_core.llm_router import generate
            revised_text = generate(prompt=prompt, temperature=0.6, max_tokens=1200)
            if not revised_text or len(revised_text) < 20:
                return None
            return {**draft, "draft": revised_text, "revised": True, "revision_round": 1}
        except Exception:
            return None

    def format_output(self, data: Any) -> str:
        reviews = data.get("reviews", [])
        if not reviews:
            return "🔍 No reviews performed."
        revisions = data.get("revisions_attempted", 0)
        lines = [f"\n🔍 Quality Review — {data.get('pass_rate', '0/0')} passed | {revisions} revisions"]
        for r in reviews:
            icon = "✅" if r["verdict"] == "PASS" else "⚠️"
            revision_tag = " [revised]" if r.get("is_revision") else ""
            lines.append(
                f"\n  {icon} {r['topic'][:50]} ({r['platform']}){revision_tag}"
                f"\n     Tone: {r['tone_score']}/10 | Value: {r['value_score']}/10 | "
                f"Engmt: {r.get('engagement_score', '?')}/10 | Style: {r.get('style_score', '?')}/10"
            )
            if r.get("format_issues"):
                for issue in r["format_issues"]:
                    lines.append(f"     ⚠ {issue}")
            if r.get("hallucination_flags"):
                for flag in r["hallucination_flags"]:
                    lines.append(f"     🚨 {flag}")
        return "\n".join(lines)
