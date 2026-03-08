import os
import logging
import httpx

class NewsletterAPI:
    def __init__(self):
        self.api_key = os.getenv("MAILCHIMP_API_KEY")
        self.server_prefix = os.getenv("MAILCHIMP_SERVER_PREFIX")
        self.list_id = os.getenv("MAILCHIMP_LIST_ID")
        self.logger = logging.getLogger("newsletter_api")
        
    def publish_campaign(self, subject: str, html_content: str) -> dict:
        if not self.api_key or not self.server_prefix:
            self.logger.info(f"[DRY RUN] Newsletter Campaign: {subject}")
            return {"status": "dry_run", "message": "Mailchimp credentials missing."}
            
        try:
            url = f"https://{self.server_prefix}.api.mailchimp.com/3.0/campaigns"
            # 1. Create campaign
            camp = httpx.post(url, auth=("anystring", self.api_key), json={
                "type": "regular",
                "recipients": {"list_id": self.list_id},
                "settings": {"subject_line": subject, "title": subject, "from_name": "JAN AI", "reply_to": "info@example.com"}
            })
            camp.raise_for_status()
            camp_id = camp.json().get("id")
            
            # 2. Set content
            content_url = f"{url}/{camp_id}/content"
            content = httpx.put(content_url, auth=("anystring", self.api_key), json={"html": html_content})
            content.raise_for_status()
            
            # 3. Send
            send_url = f"{url}/{camp_id}/actions/send"
            send = httpx.post(send_url, auth=("anystring", self.api_key))
            send.raise_for_status()
            
            return {"status": "sent", "campaign_id": camp_id}
        except Exception as e:
            self.logger.error(f"Newsletter send failed: {e}")
            return {"status": "error", "message": str(e)}
