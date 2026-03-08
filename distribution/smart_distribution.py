import logging
from typing import Dict, Any

logger = logging.getLogger("smart_distribution")

class SmartDistributionEngine:
    """
    Analyzes a successful piece of content and automatically 
    repurposes and routes it to other appropriate platforms.
    """
    def __init__(self, brand_id: int):
        self.brand_id = brand_id
        
    def analyze_best_platform(self, topic: str, content_type: str) -> str:
        """
        Infers the highest ROI platform based on the topic and format.
        """
        if content_type == "video" or "tutorial" in topic.lower():
            return "youtube"
        if "thread" in content_type or "news" in topic.lower():
            return "twitter"
        if "professional" in topic.lower() or "b2b" in topic.lower():
            return "linkedin"
        return "newsletter"
        
    def generate_repurpose_strategy(self, source_platform: str, content_id: int) -> list:
        """
        Takes a successful post ID and maps out how to convert it 
        for other distribution nodes.
        """
        logger.info(f"Generating repurpose mapping for {source_platform} post {content_id}...")
        
        repurpose_map = []
        if source_platform == "youtube":
            repurpose_map = [
                {"target": "twitter", "format": "thread", "prompt": "Convert this video script into a 5-part Twitter thread."},
                {"target": "linkedin", "format": "carousel", "prompt": "Summarize the key takeaways into a LinkedIn carousel format."},
                {"target": "newsletter", "format": "longform", "prompt": "Expand this topic into a weekly newsletter deep-dive."}
            ]
        elif source_platform == "twitter":
            repurpose_map = [
                {"target": "linkedin", "format": "text_post", "prompt": "Adapt this short thread into a professional LinkedIn post."}
            ]
            
        return repurpose_map

    def execute_distribution(self, content_data: Dict[str, Any]):
        """
        Orchestrates parallel publishing across appropriate connectors.
        """
        target = self.analyze_best_platform(content_data.get("topic", ""), content_data.get("format", "text"))
        logger.info(f"Smart distributing content to primary target: {target}")
        
        return {
            "status": "success",
            "primary_target": target,
            "repurpose_opportunities": self.generate_repurpose_strategy(target, content_id=content_data.get("id", 1))
        }
