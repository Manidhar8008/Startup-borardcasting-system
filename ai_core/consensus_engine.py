# -*- coding: utf-8 -*-
"""Consensus Engine — Multi-agent consensus for important decisions.

Spawns multiple agents with the same input, collects recommendations,
and merges results via weighted scoring.

Usage:
    from ai_core.consensus_engine import ConsensusEngine
    ce = ConsensusEngine()
    result = ce.decide(
        question="What topic should we focus on today?",
        agents=["trend", "strategy", "analytics"],
        context={"brand": "janani_ai"},
    )
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("consensus")


class ConsensusEngine:
    """Spawn multiple agents and merge their recommendations."""

    # Default weight per agent role
    ROLE_WEIGHTS = {
        "trend_intelligence": 0.30,
        "strategist": 0.30,
        "analyst": 0.20,
        "topic_intelligence": 0.20,
    }

    def __init__(self, brand: str = "janani_ai"):
        self.brand = brand

    def decide(
        self,
        question: str,
        agents: List[str],
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Run multiple agents and merge their recommendations.

        Args:
            question: The decision question.
            agents: Agent names to consult (from registry).
            context: Shared context passed to all agents.

        Returns:
            Dict with 'consensus', 'agent_results', 'confidence'.
        """
        from agents.agent_registry import get_agent

        context = context or {}
        context["question"] = question
        agent_results = []

        for agent_name in agents:
            try:
                agent = get_agent(agent_name, brand=self.brand)
                result = agent.run(**context)
                weight = self.ROLE_WEIGHTS.get(agent.role, 0.15)
                agent_results.append({
                    "agent": agent_name,
                    "role": agent.role,
                    "result": result,
                    "weight": weight,
                })
                logger.info("Agent '%s' produced result (weight=%.2f)", agent_name, weight)
            except Exception as exc:
                logger.warning("Agent '%s' failed: %s", agent_name, exc)
                agent_results.append({
                    "agent": agent_name,
                    "error": str(exc),
                    "weight": 0,
                })

        # Merge results
        consensus = self._merge(agent_results, question)
        return consensus

    def _merge(self, agent_results: List[Dict], question: str) -> Dict:
        """Merge agent results into a consensus decision."""
        # Collect all topic recommendations
        all_topics: Dict[str, float] = {}
        all_insights: List[str] = []
        total_weight = 0

        for ar in agent_results:
            if ar.get("error"):
                continue
            weight = ar.get("weight", 0.15)
            total_weight += weight
            result = ar.get("result", {})

            # Extract topics from different agent output formats
            topics = []
            if isinstance(result, dict):
                topics.extend(self._extract_topics(result))
                # Collect insights
                for key in ["strategy_insights", "learning_update", "trends"]:
                    if key in result:
                        all_insights.append(f"{ar['agent']}: {str(result[key])[:200]}")

            for topic in topics:
                name = topic.get("topic", topic.get("title", ""))
                score = topic.get("rank_score", topic.get("score", 0.5))
                if name:
                    all_topics[name] = all_topics.get(name, 0) + score * weight

        # Normalize scores
        if total_weight > 0:
            for t in all_topics:
                all_topics[t] = round(all_topics[t] / total_weight, 3)

        # Sort by consensus score
        ranked = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)
        top_3 = [{"topic": t, "consensus_score": s} for t, s in ranked[:3]]

        # Confidence based on agent agreement
        n_agents = sum(1 for ar in agent_results if not ar.get("error"))
        confidence = min(n_agents / max(len(agent_results), 1), 1.0)

        return {
            "question": question,
            "consensus_topics": top_3,
            "top_recommendation": top_3[0] if top_3 else {},
            "agent_count": n_agents,
            "confidence": round(confidence, 2),
            "insights": all_insights[:5],
            "agent_results": agent_results,
        }

    def _extract_topics(self, result: Dict) -> List[Dict]:
        """Extract topics from various agent output formats."""
        topics = []
        # TrendAgent format
        if "trends" in result:
            topics.extend(result["trends"])
        # TopicRanker format
        if "ranked_topics" in result:
            topics.extend(result["ranked_topics"])
        # StrategyAgent format
        if "plan" in result and isinstance(result["plan"], list):
            topics.extend(result["plan"])
        # Research format
        if "research_results" in result:
            topics.extend(result["research_results"])
        return topics

    def format_output(self, data: Dict) -> str:
        lines = [
            f"\n🤝 Consensus Decision",
            f"   Question: {data.get('question', '')}",
            f"   Agents consulted: {data.get('agent_count', 0)} | Confidence: {data.get('confidence', 0):.0%}",
        ]

        top = data.get("consensus_topics", [])
        if top:
            lines.append("\n   📊 Top Recommendations:")
            for i, t in enumerate(top, 1):
                lines.append(f"      {i}. {t.get('topic', '?')} (score: {t.get('consensus_score', 0):.3f})")

        insights = data.get("insights", [])
        if insights:
            lines.append("\n   💡 Key Insights:")
            for insight in insights[:3]:
                lines.append(f"      • {insight[:100]}")

        return "\n".join(lines)
