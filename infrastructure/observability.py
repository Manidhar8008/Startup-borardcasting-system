import time
import logging
from functools import wraps

"""
Observability Pipeline for JAN AI Operating System.
Tracks agent performance, pipeline health, error rates, and API latency.
Ready for Datadog / Prometheus scraping.
"""

logger = logging.getLogger("observability")

class MetricsRegistry:
    def __init__(self):
        self.counters = {}
        self.histograms = {}

    def increment(self, metric_name: str, tags: dict = None):
        tag_str = str(tags) if tags else "none"
        key = f"{metric_name}_{tag_str}"
        self.counters[key] = self.counters.get(key, 0) + 1
        
    def record_time(self, metric_name: str, duration: float, tags: dict = None):
        tag_str = str(tags) if tags else "none"
        key = f"{metric_name}_{tag_str}"
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(duration)
        
    def export_metrics(self):
        """Used by Prometheus scraper endpoint."""
        return {
            "counters": self.counters,
            "histograms": self.histograms
        }

metrics = MetricsRegistry()

def trace_agent(agent_name: str):
    """
    Decorator to wrap Agent run() methods to log latencies and errors natively.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.record_time("agent_execution_seconds", duration, {"agent": agent_name})
                metrics.increment("agent_executions_total", {"agent": agent_name, "status": "success"})
                logger.info(f"[{agent_name}] execution completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.increment("agent_executions_total", {"agent": agent_name, "status": "error"})
                metrics.increment("agent_errors_total", {"agent": agent_name, "error_type": type(e).__name__})
                logger.error(f"[{agent_name}] execution failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator
