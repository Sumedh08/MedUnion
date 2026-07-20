import random
from datetime import datetime, timedelta
from typing import Optional
from agents.base import BaseAgent, orchestrator
from core.logging import logger


class DataRetrievalAgent(BaseAgent):
    name = "data_retrieval"

    def process(self, context: dict) -> dict:
        input_data = context.get("input", {})
        query = input_data.get("query", "")
        entity_type = input_data.get("entity_type", "hospital")
        entity_id = input_data.get("entity_id")

        result = {
            "query": query,
            "data_points": self._retrieve(entity_type, entity_id),
            "timestamp": datetime.now().isoformat(),
        }
        return result

    def _retrieve(self, entity_type: str, entity_id: Optional[str]) -> list:
        from core.database import SessionLocal
        db = SessionLocal()
        try:
            if entity_type == "hospital":
                return self._get_hospital_data(db, entity_id)
            elif entity_type == "district":
                return self._get_district_data(db, entity_id)
            elif entity_type == "inventory":
                return self._get_inventory_data(db, entity_id)
            return []
        finally:
            db.close()

    def _get_hospital_data(self, db, hospital_id: Optional[str]) -> list:
        from services.hospital.adapter import HospitalAdapter
        adapter = HospitalAdapter(db)
        if hospital_id:
            kpis = adapter.compute_kpis(hospital_id)
            if kpis:
                return [
                    {"metric": "bed_occupancy", "value": kpis[0]["bed_occupancy"]["value"], "unit": "%"},
                    {"metric": "admissions_30d", "value": kpis[0]["admissions_30d"]["value"], "unit": "count"},
                    {"metric": "staff_count", "value": kpis[0]["staff_count"]["value"], "unit": "count"},
                ]
        else:
            summary = adapter.get_kpi_summary()
            if summary:
                return [
                    {"metric": "avg_bed_occupancy", "value": summary.get("avg_bed_occupancy", 0), "unit": "%"},
                    {"metric": "total_admissions_30d", "value": summary.get("total_admissions_30d", 0), "unit": "count"},
                ]
        return []

    def _get_district_data(self, db, district_id: Optional[str]) -> list:
        from services.community.adapter import CommunityAdapter
        adapter = CommunityAdapter(db)
        if district_id:
            kpis = adapter.compute_kpis(district_id)
            if kpis:
                return [
                    {"metric": "disease_incidence", "value": kpis[0]["disease_incidence"]["value"], "unit": "cases"},
                    {"metric": "vaccination_coverage", "value": kpis[0]["vaccination_coverage"]["value"], "unit": "%"},
                ]
        else:
            summary = adapter.get_kpi_summary()
            if summary:
                return [
                    {"metric": "avg_disease_incidence", "value": summary.get("avg_disease_incidence", 0), "unit": "cases"},
                    {"metric": "avg_vaccination_coverage", "value": summary.get("avg_vaccination_coverage", 0), "unit": "%"},
                ]
        return []

    def _get_inventory_data(self, db, facility_id: Optional[str]) -> list:
        from services.hospital.adapter import HospitalAdapter
        adapter = HospitalAdapter(db)
        inventory = adapter.get_inventory(facility_id)
        if inventory:
            lowest = min(inventory, key=lambda x: x.get("days_until_stockout", 999))
            return [{"metric": "days_until_stockout", "value": lowest.get("days_until_stockout", 0), "unit": "days", "item": lowest.get("medicine_name")}]
        return []


orchestrator.register(DataRetrievalAgent())
