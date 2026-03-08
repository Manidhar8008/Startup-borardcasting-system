import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.agent_registry import register
from analytics_engine.growth_intelligence import GrowthIntelligence

logger = logging.getLogger("agent.founder")

@register
class FounderAgent(BaseAgent):
    name = "founder_assistant"
    role = "Strategic Advisor & Chief of Staff"
    description = "Provides strategic advice, translates analytics into actionable insights, and acts as a sounding board."
    tools = []
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Provides advice based on query and growth data.
        
        Expected kwargs:
            query (str): The founder's question.
            brand_id (int): Brand context.
            db (Session): DB Session for analytics.
        """
        query = kwargs.get("query", "How are we doing?")
        brand_id = kwargs.get("brand_id")
        db = kwargs.get("db")
        
        if not db or not brand_id:
            return {"advice": "I need database access and a brand context to give advice."}
            
        gi = GrowthIntelligence(db)
        perf = gi.get_brand_performance(brand_id)
        
        # Using the base LLM router from the framework.
        try:
            from ai_core.llm_router import get_provider
            llm = get_provider()
        except ImportError:
            llm = None
            
        prompt = f"""
        You are a top-tier Chief of Staff and Growth Advisor for a SaaS startup.
        
        Analytics (Last 30 Days):
        Views: {perf['metrics']['views']}
        Likes: {perf['metrics']['likes']}
        Best Platform: {perf.get('best_format', 'Unknown')}
        
        Founder's Prompt: {query}
        
        Provide strategic, actionable advice based on the data.
        """
        
        if llm:
            try:
                response = llm.generate(prompt)
                advice = response.get("content", "I am unable to process the data right now.")
            except Exception as e:
                logger.error(f"FounderAgent LLM error: {e}")
                advice = f"Simulated Advice: Based on your best platform ({perf.get('best_format')}), you should post at 9 AM EST on Tuesdays."
        else:
            advice = f"Simulated Advice: System is currently running without LLM. Insights point to focusing on {perf.get('best_format')} platform due to higher engagement."
            
        return {
            "query": query,
            "performance_context": perf,
            "advice": advice
        }
