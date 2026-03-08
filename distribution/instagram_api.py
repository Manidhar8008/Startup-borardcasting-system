import os
import httpx
import logging

class InstagramAPI:
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.logger = logging.getLogger("instagram_api")

    def publish_post(self, image_url: str, caption: str) -> dict:
        if not self.access_token or not self.account_id:
            self.logger.info(f"[DRY RUN] Instagram Post: {caption} | Image: {image_url}")
            return {"status": "dry_run", "message": "Instagram credentials missing, running in dry-run mode."}

        try:
            # 1. Create media container
            url = f"https://graph.facebook.com/v19.0/{self.account_id}/media"
            container_resp = httpx.post(url, params={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            })
            container_resp.raise_for_status()
            creation_id = container_resp.json().get("id")

            # 2. Publish media container
            publish_url = f"https://graph.facebook.com/v19.0/{self.account_id}/media_publish"
            pub_resp = httpx.post(publish_url, params={
                "creation_id": creation_id,
                "access_token": self.access_token
            })
            pub_resp.raise_for_status()
            
            return {"status": "published", "id": pub_resp.json().get("id")}
        except Exception as e:
            self.logger.error(f"Failed to publish to Instagram: {e}")
            return {"status": "error", "message": str(e)}
