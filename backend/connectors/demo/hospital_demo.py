from typing import Optional
from datetime import datetime, timedelta
import random

from connectors.base.base_connector import ReadOnlyConnector, ReadOnlyMixin, CapabilityStatement
from core.logging import logger


_departments = ["Emergency", "ICU", "Cardiology", "Pediatrics", "Maternity", "Orthopedics", "Neurology", "Oncology", "General Surgery", "Internal Medicine"]
_wards = ["A", "B", "C", "D", "E"]
_medicines = ["Paracetamol", "Amoxicillin", "Atorvastatin", "Metformin", "Omeprazole", "Losartan", "Salbutamol", "Insulin", "Warfarin", "Furosemide"]


class HospitalDemoConnector(ReadOnlyConnector, ReadOnlyMixin):
    """Demo data connector for Hospital Intelligence workspace.
    
    Generates a stable dataset once on connect(). All fetch methods
    return cached data — identical results across page refreshes.
    """

    name = "demo_hospital"
    DEFAULT_BED_COUNT = 500
    DEFAULT_DEPARTMENT_COUNT = 10

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._data = {}

    def connect(self) -> bool:
        self._connected = True
        self._generate_demo_data()
        logger.info(f"Hospital demo connector initialized: {len(self._data.get('hospitals', []))} hospitals, {len(self._data.get('beds', []))} beds")
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
            connector_type="demo_hospital",
            api_version="1.0.0",
            supported_resources=[
                "hospitals", "departments", "wards", "beds",
                "patients", "encounters", "admissions",
                "observations", "medications", "staff",
                "equipment", "operating_rooms", "emergency_visits",
                "medicine_inventory",
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

        self._data["hospitals"] = [
            {"id": "HOSP-001", "name": "University Medical Center", "type": "teaching", "campus_count": 2, "total_beds": 800, "active": True},
            {"id": "HOSP-002", "name": "City General Hospital", "type": "district", "campus_count": 1, "total_beds": 450, "active": True},
            {"id": "HOSP-003", "name": "Northside Community Hospital", "type": "community", "campus_count": 1, "total_beds": 200, "active": True},
            {"id": "HOSP-004", "name": "Children's Medical Center", "type": "specialty", "campus_count": 1, "total_beds": 300, "active": True},
            {"id": "HOSP-005", "name": "Regional Heart Institute", "type": "specialty", "campus_count": 1, "total_beds": 250, "active": True},
        ]

        self._data["departments"] = []
        for i, dept in enumerate(_departments, 1):
            hosp_id = rng.choice(self._data["hospitals"])["id"]
            self._data["departments"].append({
                "id": f"DEPT-{i:03d}", "hospital_id": hosp_id, "name": dept, "ward_count": rng.randint(1, 3)
            })

        self._data["wards"] = []
        self._data["beds"] = []
        bed_id = 1
        for dept in self._data["departments"]:
            for w in _wards:
                ward_id = f"WARD-{dept['id']}-{w}"
                self._data["wards"].append({"id": ward_id, "department_id": dept["id"], "name": f"Ward {w}", "bed_count": 20})
                for b in range(1, 21):
                    self._data["beds"].append({
                        "id": f"BED-{bed_id:05d}", "ward_id": ward_id, "label": f"{w}-{b:02d}",
                        "status": rng.choice(["occupied", "available", "maintenance", "reserved"]),
                        "patient_id": f"PAT-{rng.randint(1000, 9999)}" if rng.random() < 0.7 else None,
                    })
                    bed_id += 1

        self._data["patients"] = []
        for i in range(1, 51):
            self._data["patients"].append({
                "id": f"PAT-{i:05d}", "age": rng.randint(1, 95),
                "gender": rng.choice(["male", "female"]),
                "department_id": rng.choice(self._data["departments"])["id"],
            })

        self._data["encounters"] = []
        for i in range(1, 201):
            start = datetime.now() - timedelta(days=rng.randint(0, 30))
            self._data["encounters"].append({
                "id": f"ENC-{i:06d}", "patient_id": f"PAT-{rng.randint(1000, 9999)}",
                "type": rng.choice(["inpatient", "outpatient", "emergency"]),
                "start": start.isoformat(),
                "end": (start + timedelta(hours=rng.randint(1, 72))).isoformat() if rng.random() < 0.7 else None,
                "department_id": rng.choice(self._data["departments"])["id"],
            })

        self._data["admissions"] = []
        for i in range(1, 151):
            admitted = datetime.now() - timedelta(days=rng.randint(0, 14))
            self._data["admissions"].append({
                "id": f"ADM-{i:06d}", "patient_id": f"PAT-{rng.randint(1000, 9999)}",
                "admitted_at": admitted.isoformat(),
                "discharged_at": (admitted + timedelta(days=rng.randint(1, 7))).isoformat() if rng.random() < 0.5 else None,
                "department_id": rng.choice(self._data["departments"])["id"],
                "diagnosis": rng.choice(["Chest pain", "Fracture", "Pneumonia", "Appendicitis", "Stroke"]),
            })

        self._data["observations"] = []
        for i in range(1, 501):
            self._data["observations"].append({
                "id": f"OBS-{i:06d}", "patient_id": f"PAT-{rng.randint(1000, 9999)}",
                "code": rng.choice(["blood-pressure", "heart-rate", "temperature", "respiratory-rate", "oxygen-saturation"]),
                "value": round(rng.uniform(60, 180), 1),
                "unit": rng.choice(["mmHg", "bpm", "°C", "/min", "%"]),
                "recorded_at": (datetime.now() - timedelta(hours=rng.randint(0, 72))).isoformat(),
            })

        self._data["medications"] = []
        for i in range(1, 301):
            self._data["medications"].append({
                "id": f"MED-{i:06d}", "medicine_name": rng.choice(_medicines),
                "patient_id": f"PAT-{rng.randint(1000, 9999)}",
                "dosage": f"{rng.randint(1, 3)}x {rng.choice([5, 10, 20, 50, 100])}mg",
                "status": rng.choice(["active", "completed", "discontinued"]),
                "prescribed_at": (datetime.now() - timedelta(days=rng.randint(0, 30))).isoformat(),
            })

        roles = ["Doctor", "Nurse", "Technician", "Administrator", "Pharmacist", "Surgeon", "Anesthesiologist"]
        self._data["staff"] = []
        for i in range(1, 101):
            self._data["staff"].append({
                "id": f"STF-{i:04d}", "name": f"Staff {i}",
                "role": rng.choice(roles),
                "department_id": rng.choice(self._data["departments"])["id"],
                "active": rng.random() < 0.9,
            })

        eq_types = ["MRI", "CT Scanner", "X-Ray", "Ultrasound", "Ventilator", "Defibrillator", "ECG Machine", "Infusion Pump"]
        self._data["equipment"] = []
        for i in range(1, 51):
            self._data["equipment"].append({
                "id": f"EQ-{i:04d}", "type": rng.choice(eq_types),
                "department_id": rng.choice(self._data["departments"])["id"],
                "status": rng.choice(["operational", "maintenance", "offline", "calibrating"]),
                "last_maintenance": (datetime.now() - timedelta(days=rng.randint(0, 90))).isoformat(),
            })

        self._data["medicine_inventory"] = []
        for i in range(1, 31):
            self._data["medicine_inventory"].append({
                "id": f"INV-{i:04d}",
                "department_id": rng.choice(self._data["departments"])["id"],
                "medicine_name": rng.choice(_medicines),
                "stock_current": rng.randint(0, 200),
                "stock_max": 200,
                "consumption_rate": round(rng.uniform(1, 30), 1),
                "days_until_stockout": round(rng.uniform(0, 60), 1),
                "unit": rng.choice(["tablets", "vials", "bottles", "ampules"]),
            })

    def _fetch_hospitals(self, **kwargs) -> list[dict]:
        return self._data.get("hospitals", [])

    def _fetch_departments(self, hospital_id: str = None, **kwargs) -> list[dict]:
        depts = self._data.get("departments", [])
        if hospital_id:
            depts = [d for d in depts if d["hospital_id"] == hospital_id]
        return depts

    def _fetch_wards(self, department_id: str = None, **kwargs) -> list[dict]:
        wards = self._data.get("wards", [])
        if department_id:
            wards = [w for w in wards if w["department_id"] == department_id]
        return wards

    def _fetch_beds(self, ward_id: str = None, status: str = None, **kwargs) -> list[dict]:
        beds = self._data.get("beds", [])
        if ward_id:
            beds = [b for b in beds if b["ward_id"] == ward_id]
        if status:
            beds = [b for b in beds if b["status"] == status]
        return beds

    def _fetch_patients(self, limit: int = 50, **kwargs) -> list[dict]:
        return self._data.get("patients", [])[:limit]

    def _fetch_encounters(self, **kwargs) -> list[dict]:
        return self._data.get("encounters", [])

    def _fetch_admissions(self, **kwargs) -> list[dict]:
        return self._data.get("admissions", [])

    def _fetch_observations(self, **kwargs) -> list[dict]:
        return self._data.get("observations", [])

    def _fetch_medications(self, **kwargs) -> list[dict]:
        return self._data.get("medications", [])

    def _fetch_staff(self, **kwargs) -> list[dict]:
        return self._data.get("staff", [])

    def _fetch_equipment(self, **kwargs) -> list[dict]:
        return self._data.get("equipment", [])

    def _fetch_medicine_inventory(self, **kwargs) -> list[dict]:
        return self._data.get("medicine_inventory", [])
