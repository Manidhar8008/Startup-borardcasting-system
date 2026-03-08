# -*- coding: utf-8 -*-
"""LinkedIn API Connector for JAN AI Media Manager.

Handles authenticating and publishing text posts to LinkedIn.
"""

import os
import httpx
from typing import Dict, Any, Optional

class LinkedInAPI:
    """Connects to LinkedIn Share API v2."""
    
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.person_id = os.getenv("LINKEDIN_PERSON_ID") # URN, e.g. "urn:li:person:12345"
        self.api_url = "https://api.linkedin.com/v2/ugcPosts"

    def is_configured(self) -> bool:
        """Returns True if LinkedIn API keys are available."""
        return bool(self.access_token and self.person_id)

    def publish_post(self, text: str) -> Dict[str, Any]:
        """Publishes a text post to LinkedIn."""
        if not self.is_configured():
            return {"status": "error", "message": "LinkedIn credentials not configured."}
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        
        payload = {
            "author": self.person_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            r = httpx.post(self.api_url, headers=headers, json=payload, timeout=10.0)
            if r.status_code == 201:
                return {"status": "success", "id": r.headers.get("x-restli-id")}
            else:
                return {"status": "error", "message": r.text, "code": r.status_code}
        except httpx.RequestError as e:
            return {"status": "error", "message": str(e)}
