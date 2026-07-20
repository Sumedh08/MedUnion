import random
from datetime import datetime
from agents.base import BaseAgent, orchestrator
from core.logging import logger


class AnalyticsAgent(BaseAgent):
    name = "analytics"

    def process(self, context: dict) -> dict:
        data = context.get("intermediate", {}).get("data_retrieval", {})
        data_points = data.get("data_points", [])

        kpis = self._compute_kpis(data_points)
        anomalies = self._detect_anomalies(data_points)
        trends = self._analyze_trends(data_points)

        result = {
            "kpis": kpis,
            "anomalies": anomalies,
            "trends": trends,
            "summary": self._generate_summary(kpis, anomalies),
            "timestamp": datetime.now().isoformat(),
        }
        return result

    def _compute_kpis(self, data_points: list) -> list:
        kpis = []
        for dp in data_points:
            metric = dp.get("metric")
            value = dp.get("value")
            if metric == "bed_occupancy" or metric == "avg_bed_occupancy":
                status = "critical" if value >= 90 else "warning" if value >= 80 else "normal"
                kpis.append({"name": metric, "value": value, "benchmark": 85.0, "status": status})
            elif metric == "disease_incidence" or metric == "avg_disease_incidence":
                status = "critical" if value >= 100 else "warning" if value >= 50 else "normal"
                kpis.append({"name": metric, "value": value, "benchmark": 50.0, "status": status})
            elif metric == "days_until_stockout":
                status = "critical" if value <= 7 else "warning" if value <= 14 else "normal"
                kpis.append({"name": metric, "value": value, "benchmark": 14.0, "status": status})
            else:
                kpis.append({"name": metric, "value": value, "benchmark": None, "status": "normal"})
        return kpis

    def _detect_anomalies(self, data_points: list) -> list:
        anomalies = []
        for dp in data_points:
            metric = dp.get("metric")
            value = dp.get("value")
            if (metric == "bed_occupancy" or metric == "avg_bed_occupancy") and value >= 90:
                anomalies.append({
                    "metric": metric,
                    "severity": "high",
                    "description": f"Critical occupancy level: {value}%",
                    "deviation_pct": round(value - 85.0, 1),
                })
            elif (metric == "disease_incidence" or metric == "avg_disease_incidence") and value >= 100:
                anomalies.append({
                    "metric": metric,
                    "severity": "high",
                    "description": f"High disease incidence: {value} cases",
                    "deviation_pct": round(((value - 50.0) / 50.0) * 100, 1) if value > 50 else 0,
                })
            elif metric == "days_until_stockout" and value <= 7:
                anomalies.append({
                    "metric": metric,
                    "severity": "high",
                    "description": f"Critical stockout risk: {value} days remaining",
                    "deviation_pct": round(((14.0 - value) / 14.0) * 100, 1),
                })
        return anomalies

    def _analyze_trends(self, data_points: list) -> list:
        trends = []
        for dp in data_points:
            metric = dp.get("metric")
            value = dp.get("value")
            if metric == "bed_occupancy" or metric == "avg_bed_occupancy":
                direction = "up" if value > 85 else "stable"
                trends.append({"metric": metric, "direction": direction, "change_pct": 0})
            elif metric == "disease_incidence" or metric == "avg_disease_incidence":
                direction = "up" if value > 50 else "stable"
                trends.append({"metric": metric, "direction": direction, "change_pct": 0})
        return trends

    def _generate_summary(self, kpis: list, anomalies: list) -> str:
        parts = []
        for kpi in kpis[:2]:
            parts.append(f"{kpi['name']} at {kpi['value']}")
        if anomalies:
            parts.append(f"{len(anomalies)} anomaly detected")
        return " | ".join(parts) if parts else "Normal operations"


orchestrator.register(AnalyticsAgent())
