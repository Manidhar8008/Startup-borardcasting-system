import os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from agents.agent_registry import register

@register
class MarketingBrainAgent(BaseAgent):
    name = "marketing_brain_agent"
    role = "marketing_os_meta_orchestrator"
    description = (
        "The highest-level meta-agent. Decides daily strategy, allocates pipeline tasks "
        "to the ControllerAgent, monitors enterprise scale performance, and triggers autonomous growth mode loops."
    )
    tools = []
    
    def __init__(self, brand: str = "janani_ai", **kwargs):
        super().__init__(brand=brand, **kwargs)
        
    def analyze_global_state(self, brand_id: int) -> Dict[str, Any]:
        """
        Pull health metrics, growth recommendations, and viral predictions.
        """
        try:
            from database.session import get_db
            from analytics_engine.growth_optimizer import GrowthOptimizer
            
            db = next(get_db())
            opt = GrowthOptimizer(db)
            recs = opt.get_recommendations(brand_id)
            db.close()
            return recs
        except Exception:
            return {"status": "Database unavailable for structural read."}

    def determine_daily_strategy(self, state: Dict[str, Any]) -> str:
        """
        Synthesize the state into actionable directives for the ControllerAgent.
        """
        if "strategies" in state:
            strat_str = "\n".join(state["strategies"])
            return f"Strategic Directives for today based on Growth ML:\n{strat_str}"
        return "Standard operating procedure: 2 LinkedIn Posts, 1 Twitter Thread based on morning research."

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the marketing brain loop.
        """
        brand_id = kwargs.get("brand_id", 1)
        
        # 1. Evaluate
        global_state = self.analyze_global_state(brand_id)
        
        # 2. Think (Meta-Strategy)
        strategy = self.determine_daily_strategy(global_state)
        
        # 3. Act (Delegate to Controller)
        return {
            "meta_strategy_status": "Active",
            "global_state_snapshot": global_state,
            "orchestration_directive": strategy
        }
        
    def format_output(self, data: Any) -> str:
        d = data.get("orchestration_directive", "Running...")
        return f"🧠 Marketing Brain Directive:\n{d}"
