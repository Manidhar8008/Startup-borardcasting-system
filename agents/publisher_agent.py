# -*- coding: utf-8 -*-
"""Publisher Agent (v2) — Publishes drafts and records topic usage.

Refactored to inherit from BaseAgent and register with the agent registry.
Delegates core logic to existing distribution/publisher_router.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_registry import register
from distribution import publisher_router
from memory import topic_memory

try:
    from distribution.linkedin_api import LinkedInAPI
except ImportError:
    LinkedInAPI = None

try:
    from distribution.twitter_api import TwitterAPI
except ImportError:
    TwitterAPI = None

try:
    from distribution.instagram_api import InstagramAPI
except ImportError:
    InstagramAPI = None

try:
    from distribution.youtube_api import YouTubeAPI
except ImportError:
    YouTubeAPI = None

try:
    from distribution.newsletter_api import NewsletterAPI
except ImportError:
    NewsletterAPI = None

logger = logging.getLogger("agent.publisher")


@register
class PublisherAgent(BaseAgent):
    name = "publisher"
    role = "publisher"
    description = (
        "Formats content, posts to platforms, and schedules publishing. "
        "Records topic usage in memory after each publish."
    )
    tools = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Publish drafts to target channels.

        Expected kwargs:
            drafts (list): Draft dicts from the content agent.
            dry_run (bool): Simulate publishing (default: True).

        Returns:
            Dict with 'publish_results' (list of result dicts).
        """
        drafts = kwargs.get("drafts", [])
        dry_run = kwargs.get("dry_run", True)

        if not drafts:
            return {"publish_results": [], "error": "No drafts to publish."}

        results = []
        timestamp = datetime.utcnow().isoformat() + "Z"

        for draft in drafts:
            content_type = draft.get("content_type", "insight")
            channels = publisher_router.route(content_type)
            topic = draft.get("topic", "Untitled")
            brand = draft.get("brand", self.brand)

            result = {
                "topic": topic,
                "brand": brand,
                "content_type": content_type,
                "channels": channels,
                "status": "simulated",
                "published_at": timestamp,
                "dry_run": dry_run,
                "api_responses": {}
            }
            
            # Live publishing
            if not dry_run:
                # Use draft platform if provided, otherwise default channels
                target_platforms = [draft.get("platform")] if draft.get("platform") else channels
                result["status"] = "published"
                
                content = draft.get("draft") or draft.get("content", "")
                
                if "linkedin" in target_platforms and LinkedInAPI:
                    li = LinkedInAPI()
                    if li.is_configured():
                        li_res = li.publish_post(content)
                        result["api_responses"]["linkedin"] = li_res
                        if li_res.get("status") == "error":
                            result["status"] = "partial_error"
                            logger.error(f"LinkedIn API error: {li_res}")
                            
                if "twitter" in target_platforms and TwitterAPI:
                    tw = TwitterAPI()
                    if tw.is_configured():
                        # Simple detection for thread vs single
                        if "\n\n" in content and len(content) > 300:
                            tweets = content.split("\n\n")
                            tw_res = tw.publish_thread(tweets)
                        else:
                            tw_res = tw.publish_tweet(content)
                        result["api_responses"]["twitter"] = tw_res
                        if tw_res.get("status") == "error":
                            result["status"] = "partial_error"
                            logger.error(f"Twitter API error: {tw_res}")

                if "instagram" in target_platforms and InstagramAPI:
                    ig = InstagramAPI()
                    # Assuming image_url in draft or blank
                    ig_res = ig.publish_post(image_url=draft.get("image_url", ""), caption=content)
                    result["api_responses"]["instagram"] = ig_res
                    if ig_res.get("status") == "error":
                        result["status"] = "partial_error"
                        logger.error(f"Instagram API error: {ig_res}")

                if "youtube" in target_platforms and YouTubeAPI:
                    yt = YouTubeAPI()
                    yt_res = yt.publish_community_post(channel_id=draft.get("channel_id", "default"), text=content)
                    result["api_responses"]["youtube"] = yt_res
                    if yt_res.get("status") == "error":
                        result["status"] = "partial_error"
                        logger.error(f"YouTube API error: {yt_res}")

                if "newsletter" in target_platforms and NewsletterAPI:
                    nl = NewsletterAPI()
                    nl_res = nl.publish_campaign(subject=topic, html_content=content)
                    result["api_responses"]["newsletter"] = nl_res
                    if nl_res.get("status") == "error":
                        result["status"] = "partial_error"
                        logger.error(f"Newsletter API error: {nl_res}")

            results.append(result)

            # Record topic usage in memory
            perf_score = min(0.4 + len(channels) * 0.15, 1.0)
            topic_memory.record_usage(topic, brand, performance_score=perf_score)
            logger.info("Published '%s' (brand=%s, score=%.2f)", topic, brand, perf_score)

        return {"publish_results": results}

    def format_output(self, data: Any) -> str:
        results = data.get("publish_results", []) if isinstance(data, dict) else data
        if not results:
            return "📤 No publications."
        mode = "🔵 DRY-RUN" if results[0].get("dry_run") else "🚀 LIVE"
        lines = [f"\n📤 Publishing Results [{mode}] — {len(results)} item(s):"]
        for r in results:
            channels_str = ", ".join(r.get("channels", []))
            lines.append(
                f"  ✅ {r['topic'][:60]}"
                f"\n     → Channels : {channels_str}"
                f"\n     → Status   : {r['status']}"
                f"\n     → Brand    : {r['brand']}"
            )
        return "\n".join(lines)


# ── Backward compatibility ────────────────────────────────────────────────────

def run(drafts: List[Dict], *, dry_run: bool = True) -> List[Dict]:
    """Legacy API: publish drafts."""
    agent = PublisherAgent()
    result = agent.run(drafts=drafts, dry_run=dry_run)
    return result.get("publish_results", [])


def format_output(results: List[Dict]) -> str:
    """Legacy API: format publish results."""
    agent = PublisherAgent()
    return agent.format_output({"publish_results": results})
