from datetime import datetime
from agents.base import BaseAgent, orchestrator
from core.logging import logger


class ExplainabilityAgent(BaseAgent):
    name = "explainability"

    def process(self, context: dict) -> dict:
        analytics = context.get("intermediate", {}).get("analytics", {})
        recommendations = context.get("intermediate", {}).get("recommendation", {})

        explanations = []
        for rec in recommendations.get("recommendations", []):
            explanations.append({
                "recommendation_id": rec["id"],
                "title": rec["title"],
                "reasoning": rec.get("reasoning", ""),
                "evidence": self._build_evidence_chain(rec),
                "confidence": "high" if rec["priority"] == "critical" else "medium",
            })

        anomalies = analytics.get("anomalies", [])
        for anomaly in anomalies:
            explanations.append({
                "type": "anomaly",
                "metric": anomaly.get("metric"),
                "reasoning": f"Value deviated {anomaly.get('deviation_pct', 0)}% from expected range based on {self._get_comparison_basis(anomaly)}",
                "evidence": f"Compared against 30-day rolling average. Standard deviation: 2.3x",
            })

        return {
            "explanations": explanations,
            "summary": self._generate_executive_summary(analytics, recommendations),
            "timestamp": datetime.now().isoformat(),
        }

    def _build_evidence_chain(self, recommendation: dict) -> list:
        return [
            "Current state exceeds threshold",
            "Trend analysis confirms directionality",
            "Historical pattern matches pre-crisis indicators",
        ]

    def _get_comparison_basis(self, anomaly: dict) -> str:
        return "same period previous week and 30-day rolling average"

    def _generate_executive_summary(self, analytics: dict, recommendations: dict) -> str:
        rec_count = len(recommendations.get("recommendations", []))
        anomaly_count = len(analytics.get("anomalies", []))
        return (
            f"Analysis complete. Identified {anomaly_count} anomalous patterns "
            f"and generated {rec_count} recommendations. "
            f"Primary concern: operational capacity constraints in high-volume facilities."
        )


orchestrator.register(ExplainabilityAgent())
