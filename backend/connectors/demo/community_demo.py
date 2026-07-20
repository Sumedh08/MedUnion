from typing import Optional
from datetime import datetime, timedelta
import random

from connectors.base.base_connector import ReadOnlyConnector, ReadOnlyMixin, CapabilityStatement
from core.logging import logger


_countries = ["Country A"]
_provinces = ["Province Alpha", "Province Beta", "Province Gamma"]
_districts = ["District North", "District South", "District East", "District West", "District Central"]
_diseases = ["Malaria", "Dengue", "Tuberculosis", "HIV/AIDS", "Diabetes", "Hypertension", "Acute Diarrhea", "Pneumonia"]
_programs = ["Immunization", "Maternal Health", "Child Health", "HIV/TB", "Malaria Control", "Nutrition"]
_indicators = ["vaccination_coverage", "disease_incidence", "treatment_success", "reporting_completeness", "mortality_rate"]


class CommunityDemoConnector(ReadOnlyConnector, ReadOnlyMixin):
    """Demo data connector for Community Health Intelligence workspace.

    Generates a stable dataset once on connect(). All fetch methods
    return cached data — identical results across page refreshes.
    """

    name = "demo_community"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._data = {}

    def connect(self) -> bool:
        self._connected = True
        self._generate_demo_data()
        logger.info(f"Community demo connector initialized: {len(self._data.get('districts', []))} districts, {len(self._data.get('facilities', []))} facilities")
        return True

    def disconnect(self):
        self._connected = False

    def health_check(self) -> dict:
        return {
            "status": "healthy",
            "connector": self.name,
            "mode": "demo_import",
            "message": "Demo data provider — stable dataset for import",
        }

    def discover_capabilities(self) -> CapabilityStatement:
        statement = CapabilityStatement(
            connector_type="demo_community",
            api_version="1.0.0",
            supported_resources=[
                "countries", "provinces", "districts", "facilities",
                "disease_reports", "indicators", "programs",
                "vaccinations", "medicine_stock", "health_workers",
                "outbreaks", "surveillance_events",
            ],
            supported_operations=["read", "search"],
            metadata={"data_origin": "synthetic_demo", "geography": "agnostic"},
        )
        self._capabilities = statement
        return statement

    def fetch(self, resource: str, params: Optional[dict] = None) -> list[dict]:
        self.assert_read_only("GET")
        params = params or {}
        method = getattr(self, f"_fetch_{resource}", None)
        if method:
            return method(**params)
        logger.warning(f"Unknown resource: {resource}")
        return []

    def _generate_demo_data(self):
        rng = random.Random(42)

        self._data["countries"] = [{"id": "COUNTRY-001", "name": c, "province_count": len(_provinces)} for c in _countries]

        self._data["provinces"] = [
            {"id": f"PROV-{i:03d}", "name": p, "country_id": "COUNTRY-001", "district_count": len(_districts)}
            for i, p in enumerate(_provinces, 1)
        ]

        self._data["districts"] = [
            {"id": f"DIST-{i:03d}", "name": d, "province_id": f"PROV-{(i % 3) + 1:03d}", "facility_count": rng.randint(5, 20)}
            for i, d in enumerate(_districts, 1)
        ]

        types = ["Hospital", "Clinic", "Health Center", "Dispensary", "Laboratory"]
        self._data["facilities"] = []
        for i in range(1, 31):
            self._data["facilities"].append({
                "id": f"FAC-{i:04d}", "name": f"Health Facility {i}",
                "type": rng.choice(types),
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "active": rng.random() < 0.9,
                "latitude": round(rng.uniform(-10, 10), 6),
                "longitude": round(rng.uniform(-10, 10), 6),
            })

        self._data["disease_reports"] = []
        for disease in _diseases:
            for _ in range(3):
                self._data["disease_reports"].append({
                    "id": f"DR-{rng.randint(10000, 99999)}",
                    "disease": disease,
                    "district_id": f"DIST-{rng.randint(1, 5):03d}",
                    "confirmed": rng.randint(0, 200),
                    "suspected": rng.randint(0, 50),
                    "deaths": rng.randint(0, 5),
                    "recovered": rng.randint(0, 150),
                    "reporting_week": f"W{rng.randint(1, 30):02d}",
                    "reported_at": (datetime.now() - timedelta(days=rng.randint(0, 30))).isoformat(),
                })

        self._data["indicators"] = []
        for i, name in enumerate(_indicators, 1):
            self._data["indicators"].append({
                "id": f"IND-{i:04d}", "name": name,
                "value": round(rng.uniform(0, 100), 1),
                "target": 80.0,
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "period": "monthly",
                "recorded_at": (datetime.now() - timedelta(days=rng.randint(0, 30))).isoformat(),
            })

        self._data["programs"] = [
            {
                "id": f"PROG-{i:03d}", "name": p,
                "status": rng.choice(["active", "completed", "planned"]),
                "budget": round(rng.uniform(100000, 5000000), 2),
                "coverage_pct": round(rng.uniform(40, 95), 1),
            }
            for i, p in enumerate(_programs, 1)
        ]

        vaccines = ["BCG", "OPV", "Measles", "DPT", "Hepatitis B", "Polio"]
        self._data["vaccinations"] = []
        for i in range(1, 31):
            self._data["vaccinations"].append({
                "id": f"VAC-{i:05d}", "vaccine": rng.choice(vaccines),
                "doses_administered": rng.randint(100, 5000),
                "coverage_pct": round(rng.uniform(40, 98), 1),
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "recorded_at": (datetime.now() - timedelta(days=rng.randint(0, 30))).isoformat(),
            })

        medicines = ["Artemisinin", "ORS", "IV Fluids", "Antibiotics", "Antimalarials", "ARV Drugs"]
        self._data["medicine_stock"] = []
        for i in range(1, 51):
            self._data["medicine_stock"].append({
                "id": f"STK-{i:05d}", "medicine": rng.choice(medicines),
                "stock_on_hand": rng.randint(0, 5000),
                "monthly_consumption": rng.randint(50, 1000),
                "days_of_stock": round(rng.uniform(0, 90), 1),
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "updated_at": (datetime.now() - timedelta(days=rng.randint(0, 7))).isoformat(),
            })

        roles = ["Doctor", "Nurse", "Midwife", "Community Health Worker", "Technician", "Pharmacist"]
        self._data["health_workers"] = []
        for i in range(1, 201):
            self._data["health_workers"].append({
                "id": f"HW-{i:05d}", "role": rng.choice(roles),
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "facility_id": f"FAC-{rng.randint(1, 30):04d}",
                "active": rng.random() < 0.85,
            })

        self._data["outbreaks"] = []
        for i in range(1, 6):
            self._data["outbreaks"].append({
                "id": f"OB-{i:04d}", "disease": rng.choice(_diseases),
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "status": rng.choice(["active", "contained", "monitoring"]),
                "cases": rng.randint(10, 500),
                "detected_at": (datetime.now() - timedelta(days=rng.randint(0, 14))).isoformat(),
                "risk_level": rng.choice(["low", "medium", "high", "critical"]),
            })

        self._data["surveillance_events"] = []
        for i in range(1, 101):
            self._data["surveillance_events"].append({
                "id": f"SE-{i:06d}",
                "event_type": rng.choice(["case_report", "lab_result", "death_report", "vaccination_event"]),
                "district_id": f"DIST-{rng.randint(1, 5):03d}",
                "reported_at": (datetime.now() - timedelta(days=rng.randint(0, 7))).isoformat(),
                "complete": rng.random() < 0.75,
            })

    def _fetch_countries(self, **kwargs) -> list[dict]:
        return self._data.get("countries", [])

    def _fetch_provinces(self, country_id: str = None, **kwargs) -> list[dict]:
        return self._data.get("provinces", [])

    def _fetch_districts(self, province_id: str = None, **kwargs) -> list[dict]:
        return self._data.get("districts", [])

    def _fetch_facilities(self, district_id: str = None, **kwargs) -> list[dict]:
        facs = self._data.get("facilities", [])
        if district_id:
            facs = [f for f in facs if f.get("district_id") == district_id]
        return facs

    def _fetch_disease_reports(self, district_id: str = None, **kwargs) -> list[dict]:
        reports = self._data.get("disease_reports", [])
        if district_id:
            reports = [r for r in reports if r.get("district_id") == district_id]
        return reports

    def _fetch_indicators(self, district_id: str = None, **kwargs) -> list[dict]:
        inds = self._data.get("indicators", [])
        if district_id:
            inds = [i for i in inds if i.get("district_id") == district_id]
        return inds

    def _fetch_programs(self, **kwargs) -> list[dict]:
        return self._data.get("programs", [])

    def _fetch_vaccinations(self, district_id: str = None, **kwargs) -> list[dict]:
        vax = self._data.get("vaccinations", [])
        if district_id:
            vax = [v for v in vax if v.get("district_id") == district_id]
        return vax

    def _fetch_medicine_stock(self, district_id: str = None, **kwargs) -> list[dict]:
        stock = self._data.get("medicine_stock", [])
        if district_id:
            stock = [s for s in stock if s.get("district_id") == district_id]
        return stock

    def _fetch_health_workers(self, district_id: str = None, **kwargs) -> list[dict]:
        hw = self._data.get("health_workers", [])
        if district_id:
            hw = [h for h in hw if h.get("district_id") == district_id]
        return hw

    def _fetch_outbreaks(self, **kwargs) -> list[dict]:
        return self._data.get("outbreaks", [])

    def _fetch_surveillance_events(self, **kwargs) -> list[dict]:
        return self._data.get("surveillance_events", [])
