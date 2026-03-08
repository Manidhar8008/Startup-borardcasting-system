# -*- coding: utf-8 -*-
"""Webhook notifier for the JAN AI Media Manager.

Handles sending notifications to external systems like Slack or Discord webhook URLs
when a draft enters the approval queue, allowing for remote approval.
"""

import os
import httpx
from typing import Dict, Any, Optional

class WebhookNotifier:
    """Sends HTTP POST notifications to configured external webhooks."""
    
    def __init__(self, brand: str):
        self.brand = brand
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.api_base_url = os.getenv("JAN_API_BASE_URL", "http://localhost:8000")
        
    def notify_approval_needed(self, draft_id: str, topic: str, platform: str, content: str) -> bool:
        """Sends a notification that a new draft needs approval."""
        if not self.slack_webhook and not self.discord_webhook:
            return False # No webhooks configured
            
        success = False
        
        # Approve/Reject links that hit the API server
        approve_url = f"{self.api_base_url}/webhook/approve/{draft_id}"
        reject_url = f"{self.api_base_url}/webhook/reject/{draft_id}"
        
        if self.slack_webhook:
            success = success or self._send_slack(topic, platform, content, approve_url, reject_url)
            
        if self.discord_webhook:
            success = success or self._send_discord(topic, platform, content, approve_url, reject_url)
            
        return success
        
    def _send_slack(self, topic: str, platform: str, content: str, approve_url: str, reject_url: str) -> bool:
        """Formats and sends a Slack block kit message."""
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"✅ New Draft for {platform.capitalize()}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Topic:* {topic}\n\n*Draft:*\n```{str(content)[:2000]}```"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Approve"
                            },
                            "style": "primary",
                            "url": approve_url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Reject"
                            },
                            "style": "danger",
                            "url": reject_url
                        }
                    ]
                }
            ]
        }
        
        try:
            r = httpx.post(self.slack_webhook, json=payload, timeout=5.0)
            return r.status_code == 200
        except Exception:
            return False

    def _send_discord(self, topic: str, platform: str, content: str, approve_url: str, reject_url: str) -> bool:
        """Formats and sends a Discord embed message."""
        payload = {
            "embeds": [{
                "title": f"New Draft: {platform.capitalize()}",
                "description": f"**Topic:** {topic}\n\n```{str(content)[:2000]}```\n\n[✅ Approve]({approve_url})  |  [❌ Reject]({reject_url})",
                "color": 65111
            }]
        }
        
        try:
            r = httpx.post(self.discord_webhook, json=payload, timeout=5.0)
            return r.status_code in [200, 204]
        except Exception:
            return False
