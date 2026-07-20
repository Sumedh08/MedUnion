from datetime import datetime
from agents.base import BaseAgent, orchestrator
from core.logging import logger


class RecommendationAgent(BaseAgent):
    name = "recommendation"

    def process(self, context: dict) -> dict:
        analytics = context.get("intermediate", {}).get("analytics", {})
        forecasts = context.get("intermediate", {}).get("forecasting", {})
        anomalies = analytics.get("anomalies", [])

        recommendations = self._generate_recommendations(anomalies, forecasts)
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_recommendations(self, anomalies: list, forecasts: dict) -> list:
        recs = []
        for i, anomaly in enumerate(anomalies):
            metric = anomaly.get("metric")
            if metric in ("bed_occupancy", "avg_bed_occupancy"):
                recs.append({
                    "id": f"REC-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                    "title": "Capacity Optimization",
                    "description": f"Address critical occupancy ({anomaly.get('deviation_pct')}% above benchmark) by redistributing staff or converting beds.",
                    "priority": "critical" if anomaly.get("severity") == "high" else "high",
                    "category": "capacity",
                    "reasoning": anomaly.get("description", "High occupancy detected"),
                    "expected_impact": "Reduce occupancy bottleneck and improve patient flow.",
                })
            elif metric in ("disease_incidence", "avg_disease_incidence"):
                recs.append({
                    "id": f"REC-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                    "title": "Outbreak Response",
                    "description": "Deploy rapid response teams and increase surveillance in affected areas.",
                    "priority": "critical",
                    "category": "operations",
                    "reasoning": anomaly.get("description", "High disease incidence detected"),
                    "expected_impact": "Contain outbreak and reduce transmission rate.",
                })
            elif metric == "days_until_stockout":
                recs.append({
                    "id": f"REC-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                    "title": "Inventory Restock",
                    "description": "Initiate emergency procurement for critical medicines.",
                    "priority": "critical",
                    "category": "inventory",
                    "reasoning": anomaly.get("description", "Critical stockout risk"),
                    "expected_impact": "Prevent treatment delays due to stockouts.",
                })
        
        if not recs:
            recs.append({
                "id": f"REC-{datetime.now().strftime('%Y%m%d')}-001",
                "title": "Maintain Operations",
                "description": "Current metrics are within normal parameters. Continue standard monitoring.",
                "priority": "low",
                "category": "operations",
                "reasoning": "No critical anomalies detected in the current data.",
                "expected_impact": "Sustain current operational efficiency.",
            })
            
        return recs


orchestrator.register(RecommendationAgent())
