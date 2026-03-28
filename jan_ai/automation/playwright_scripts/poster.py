from automation.playwright_scripts.reddit_poster import post_to_reddit
import logging

logger = logging.getLogger(__name__)

def auto_post_content(platform: str, topic: str, content: str) -> bool:
    logger.info(f"Core Automation router checking platform: {platform}")
    if platform.lower() == "reddit":
        return post_to_reddit(topic, content)
    else:
        logger.error(f"Platform {platform} is not live yet. Using Reddit for Production V1.")
        return False
