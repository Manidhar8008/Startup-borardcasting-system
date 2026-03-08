# -*- coding: utf-8 -*-
"""Twitter Thread Agent — Punchy, shareable threads.

Generates Twitter/X threads with:
- 280-char per tweet enforcement
- Numbered format (1/5, 2/5...)
- Hook tweet + value tweets + CTA tweet
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.agent_registry import register

TWITTER_PROMPT = """You are JAN, a Twitter/X ghostwriter for brand '{brand}'.

Write a Twitter thread (5 tweets) about: {topic}
Context: {context}

Rules:
- Tweet 1: Hook — attention-grabbing statement or question
- Tweets 2-4: Value delivery — one clear point per tweet
- Tweet 5: CTA — ask for follow, retweet, or reply
- Each tweet MUST be under 270 characters (leave room for numbering)
- Use 1/5, 2/5, 3/5 format
- Punchy, no fluff, shareable
- Use line breaks within tweets sparingly
- No hashtags except in tweet 5 (max 2)

Output exactly 5 tweets, each on its own line starting with the number format.
No preamble, no labels."""


@register
class TwitterWriter(BaseAgent):
    name = "twitter_writer"
    role = "content_creator"
    description = "Writes Twitter/X threads with punchy, shareable content under 280 chars per tweet."
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        topic = kwargs.get("topic", "AI and startups")
        context = kwargs.get("context", kwargs.get("summary", ""))
        plan = kwargs.get("plan", [])

        if plan and not kwargs.get("topic"):
            first = plan[0] if plan else {}
            topic = first.get("title", topic)
            context = first.get("summary", context)

        prompt = TWITTER_PROMPT.format(brand=self.brand, topic=topic, context=context or "No additional context.")

        try:
            from ai_core.llm_router import generate
            draft = generate(prompt=prompt, temperature=0.8, max_tokens=800)
        except Exception as exc:
            self.logger.warning("Twitter generation failed: %s", exc)
            draft = f"1/5 [Thread generation failed for: {topic}]"

        # Split into individual tweets
        tweets = [line.strip() for line in draft.splitlines() if line.strip()]

        return {
            "drafts": [{
                "brand": self.brand,
                "topic": topic,
                "platform": "twitter",
                "content_type": "twitter_thread",
                "draft": draft,
                "tweets": tweets,
                "tweet_count": len(tweets),
                "llm_generated": True,
            }],
        }

    def format_output(self, data: Any) -> str:
        drafts = data.get("drafts", [])
        if not drafts:
            return "🐦 No Twitter threads generated."
        d = drafts[0]
        lines = [f"\n🐦 Twitter Thread — {d.get('topic', '')} ({d.get('tweet_count', 0)} tweets)", ""]
        for tweet in d.get("tweets", []):
            lines.append(f"  {tweet}")
            lines.append("")
        return "\n".join(lines)
