import numpy as np
from datetime import datetime, timedelta
from agents.base import BaseAgent, orchestrator
from core.logging import logger


class ForecastingAgent(BaseAgent):
    name = "forecasting"

    def process(self, context: dict) -> dict:
        input_data = context.get("input", {})
        horizon_days = input_data.get("horizon_days", 30)
        data = context.get("intermediate", {}).get("data_retrieval", {})
        data_points = data.get("data_points", [])

        predictions = {
            "hospital_occupancy": self._forecast_occupancy(horizon_days, data_points),
            "medicine_demand": self._forecast_demand(horizon_days, data_points),
            "disease_incidence": self._forecast_disease(horizon_days, data_points),
            "confidence_intervals": self._get_confidence(),
        }

        return {
            "predictions": predictions,
            "horizon_days": horizon_days,
            "methodology": "trend_extrapolation",
            "timestamp": datetime.now().isoformat(),
        }

    def _forecast_occupancy(self, days: int, data_points: list) -> list:
        base = 70.0
        for dp in data_points:
            if dp.get("metric") in ("bed_occupancy", "avg_bed_occupancy"):
                base = dp.get("value", 70.0)
        
        result = []
        for d in range(days):
            date = (datetime.now() + timedelta(days=d)).isoformat()
            value = base + (d * 0.1) + np.sin(d / 7 * 2 * np.pi) * 2
            result.append({"date": date, "predicted": round(max(0, min(100, value)), 1)})
        return result

    def _forecast_demand(self, days: int, data_points: list) -> list:
        base = 200.0
        result = []
        for d in range(days):
            date = (datetime.now() + timedelta(days=d)).isoformat()
            value = base + (d * 0.5)
            result.append({"date": date, "predicted": round(max(0, value), 1)})
        return result

    def _forecast_disease(self, days: int, data_points: list) -> list:
        base = 20.0
        for dp in data_points:
            if dp.get("metric") in ("disease_incidence", "avg_disease_incidence"):
                base = dp.get("value", 20.0)
                
        result = []
        for d in range(days):
            date = (datetime.now() + timedelta(days=d)).isoformat()
            value = base + (d * 0.2) + np.sin(d / 14 * 2 * np.pi) * 5
            result.append({"date": date, "predicted": round(max(0, value), 1)})
        return result

    def _get_confidence(self) -> dict:
        return {"lower": 5.0, "upper": 95.0, "level": 0.95}


orchestrator.register(ForecastingAgent())
