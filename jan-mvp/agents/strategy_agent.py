"""
Strategy Agent

Responsible for developing the overarching content strategy based on an idea and business profile
using the Deepseek model via the local Ollama API.
"""
from typing import Dict, Any, Optional
from ai.ollama_client import generate

def generate_strategy(idea: str, business_profile: Dict[str, Any]) -> Optional[str]:
    """
    Generates a strategy based on the input idea and business profile.
    
    Args:
        idea: The core concept to build a strategy for.
        business_profile: A dictionary containing brand information.
        
    Returns:
        The generated strategy text string, or None if the generation fails.
    """
    prompt = f"""You are an expert social media strategist.

Business Profile:
{business_profile}

User Idea:
{idea}

Your task:
Create a social media growth strategy.

Return structured text with:
1 Topic
2 Recommended platforms (LinkedIn, YouTube, Facebook)
3 3 content angles
4 Best posting times
5 Suggested hashtags
"""

    strategy = generate(prompt, model="llama3")

    return strategy
