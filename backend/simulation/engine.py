import random
import uuid
from datetime import datetime
from typing import Optional
from core.logging import logger


class DigitalTwinEngine:
    def __init__(self):
        self.scenarios = {}
        self.active_simulations = {}

    def create_scenario(self, name: str, description: str, parameters: dict) -> dict:
        scenario_id = str(uuid.uuid4())[:8]
        scenario = {
            "id": scenario_id,
            "name": name,
            "description": description,
            "parameters": parameters,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
        }
        self.scenarios[scenario_id] = scenario
        return scenario

    def run_simulation(self, scenario_id: str) -> dict:
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return {"error": "Scenario not found"}

        params = scenario["parameters"]
        
        from core.database import SessionLocal
        db = SessionLocal()
        try:
            impacted_kpis = self._compute_impacted_kpis(db, params)
            forecasts = self._compute_forecasts(db, params)
            capacity = self._compute_capacity_impact(db, params)
            actions = self._recommend_actions(impacted_kpis, capacity)
            risk_score = self._compute_risk_score(impacted_kpis)
        finally:
            db.close()

        result = {
            "scenario_id": scenario_id,
            "scenario_name": scenario["name"],
            "impacted_kpis": impacted_kpis,
            "forecasts": forecasts,
            "capacity_impacts": capacity,
            "recommended_actions": actions,
            "risk_score": risk_score,
            "data_source": "canonical_database",
            "simulated_at": datetime.now().isoformat(),
        }
        self.active_simulations[scenario_id] = result
        return result

    def _compute_impacted_kpis(self, db, params: dict) -> list:
        from services.hospital.adapter import HospitalAdapter
        adapter = HospitalAdapter(db)
        summary = adapter.get_kpi_summary()
        base_occupancy = summary.get("avg_bed_occupancy", 70.0) if summary else 70.0
        
        kpis = []
        for key, val in params.items():
            impact = val * 1.2
            kpis.append({
                "kpi": f"{key}_impact",
                "baseline": base_occupancy if "occupancy" in key else val,
                "simulated": round(base_occupancy + impact if "occupancy" in key else val + impact, 1),
                "change_pct": round((impact / base_occupancy) * 100, 1) if base_occupancy else 0,
            })
        return kpis

    def _compute_forecasts(self, db, params: dict) -> list:
        from services.hospital.adapter import HospitalAdapter
        adapter = HospitalAdapter(db)
        summary = adapter.get_kpi_summary()
        base_occupancy = summary.get("avg_bed_occupancy", 70.0) if summary else 70.0
        
        return [{
            "metric": "occupancy_forecast",
            "baseline_30d": round(base_occupancy, 1),
            "simulated_30d": round(min(100, base_occupancy + 15.0), 1),
        }]

    def _compute_capacity_impact(self, db, params: dict) -> list:
        from services.hospital.adapter import HospitalAdapter
        adapter = HospitalAdapter(db)
        summary = adapter.get_kpi_summary()
        total_beds = summary.get("total_beds", 100) if summary else 100
        
        return [{
            "resource": "ICU Beds",
            "current_demand": int(total_beds * 0.1),
            "projected_demand": int(total_beds * 0.15),
            "gap": int(total_beds * 0.05),
        }]

    def _recommend_actions(self, kpis: list, capacity: list) -> list:
        return [
            "Increase ICU capacity by converting general wards",
            "Request staff redeployment from low-occupancy facilities",
            "Activate emergency supply chain protocol",
        ]

    def _compute_risk_score(self, kpis: list) -> float:
        return 0.75

    def list_scenarios(self) -> list:
        return list(self.scenarios.values())

    def get_simulation_result(self, scenario_id: str) -> Optional[dict]:
        return self.active_simulations.get(scenario_id)


digital_twin = DigitalTwinEngine()
