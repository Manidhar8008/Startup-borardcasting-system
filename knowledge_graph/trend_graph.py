class TrendGraph:
    """
    Maps how global trends connect to each other to project narrative arcs.
    Example: 'LLM Agents' -> 'Cost Optimization' -> 'SaaS Pricing'
    """
    def __init__(self):
        self.graph = {}
        
    def record_trend_transition(self, source_trend: str, target_trend: str, correlation: float):
        if source_trend not in self.graph:
            self.graph[source_trend] = []
        self.graph[source_trend].append({"target": target_trend, "corr": correlation})
        
    def predict_next_trend(self, current_trend: str) -> str:
        if current_trend in self.graph:
            targets = self.graph[current_trend]
            best = max(targets, key=lambda x: x["corr"])
            return best["target"]
        return "general_automation"
