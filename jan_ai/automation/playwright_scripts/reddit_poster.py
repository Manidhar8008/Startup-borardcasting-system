from playwright.sync_api import sync_playwright
import time
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

USER_DATA_DIR = os.path.join(os.getcwd(), "playwright_user_data")

def post_to_reddit(topic: str, content: str) -> bool:
    try:
        with sync_playwright() as p:
            logger.info(">>> REDDIT AUTOMATION STARTED <<<")
            logger.info(f"Using persistent browser session at: {USER_DATA_DIR}")
            
            # headless=False allows the human to intervene and solve Captchas and see the progress
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()
            
            # Navigate to standard submit URL (using /r/test to avoid getting banned for automation)
            logger.info(f"Navigating to Reddit submission screen...")
            page.goto("https://www.reddit.com/r/test/submit", wait_until="networkidle")
            
            # --- LOGIN CHECK ---
            if page.locator('a[href*="login"]').is_visible() or page.locator('button:has-text("Log In")').is_visible():
                logger.error("Reddit profile is NOT logged in!")
                logger.error("ACTION REQUIRED: Log in manually to this Chrome window. Automation paused for 60 seconds.")
                # Give user time to log in once, the cookie is saved in user_data_dir for next time
                time.sleep(60)
                
            # Wait for the post elements to appear
            page.wait_for_selector('textarea[placeholder="Title"], input[placeholder="Title"], textarea[name="title"]', timeout=30000)
            
            logger.info("Executing Form Fill: Title...")
            title_area = page.locator('textarea[placeholder="Title"], input[placeholder="Title"], textarea[name="title"]').first
            title_area.fill(topic[:300]) # Reddit title limit
            
            logger.info("Executing Form Fill: Body Content...")
            # Click the Rich Text editor
            content_area = page.locator('div[contenteditable="true"]').first
            content_area.click()
            page.keyboard.type(content)
            
            logger.info("Executing Submission...")
            submit_btn = page.locator('button:has-text("Post")').last
            submit_btn.click()
            
            logger.info("Post submitted! Waiting for Reddit server confirmation...")
            time.sleep(5)
            
            logger.info(">>> REDDIT AUTOMATION SUCCESSFUL <<<")
            context.close()
            return True
            
    except Exception as e:
        logger.error(f"Reddit Automation Crashed: {str(e)}")
        return False
