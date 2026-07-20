"""Canonical resource contracts — Pydantic validation for import loads."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CanonicalBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(min_length=1, max_length=50)


class HospitalContract(CanonicalBase):
    name: str = Field(min_length=1)
    type: Optional[str] = None
    campus_count: Optional[int] = 1
    total_beds: Optional[int] = 0
    active: Optional[bool] = True


class DepartmentContract(CanonicalBase):
    name: str = Field(min_length=1)
    hospital_id: Optional[str] = None
    building_id: Optional[str] = None
    specialty: Optional[str] = None
    ward_count: Optional[int] = 1


class WardContract(CanonicalBase):
    department_id: Optional[str] = None
    name: str = Field(min_length=1)
    bed_count: Optional[int] = 0


class BedContract(CanonicalBase):
    ward_id: str
    label: Optional[str] = None
    status: Optional[str] = "available"
    patient_id: Optional[str] = None


class PatientContract(CanonicalBase):
    age: Optional[int] = None
    gender: Optional[str] = None
    hospital_id: Optional[str] = None


class AdmissionContract(CanonicalBase):
    patient_id: str
    department_id: Optional[str] = None
    ward_id: Optional[str] = None
    bed_id: Optional[str] = None
    admitted_at: Optional[str] = None
    discharged_at: Optional[str] = None
    diagnosis: Optional[str] = None
    outcome: Optional[str] = None
    length_of_stay_days: Optional[float] = None


class StaffContract(CanonicalBase):
    name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[str] = None
    active: Optional[bool] = True


class EquipmentContract(CanonicalBase):
    department_id: Optional[str] = None
    equipment_type: Optional[str] = None
    status: Optional[str] = None
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None


class MedicineInventoryContract(CanonicalBase):
    department_id: Optional[str] = None
    medicine_name: Optional[str] = None
    stock_current: Optional[float] = None
    stock_max: Optional[float] = None
    consumption_rate: Optional[float] = None
    days_until_stockout: Optional[float] = None
    unit: Optional[str] = "units"


class DistrictContract(CanonicalBase):
    name: str = Field(min_length=1)
    county_id: Optional[str] = None
    code: Optional[str] = None
    population: Optional[int] = 0


class FacilityContract(CanonicalBase):
    district_id: str
    name: str = Field(min_length=1)
    type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active: Optional[bool] = True


class DiseaseCaseContract(CanonicalBase):
    district_id: str
    disease_id: Optional[str] = None
    confirmed: Optional[int] = 0
    suspected: Optional[int] = 0
    deaths: Optional[int] = 0
    recovered: Optional[int] = 0
    reporting_week: Optional[str] = None
    reported_at: Optional[str] = None


class OutbreakContract(CanonicalBase):
    district_id: str
    disease_id: Optional[str] = None
    status: Optional[str] = None
    cases: Optional[int] = 0
    risk_level: Optional[str] = None
    detected_at: Optional[str] = None
    contained_at: Optional[str] = None


class HealthWorkerContract(CanonicalBase):
    district_id: Optional[str] = None
    facility_id: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = True


class VaccinationContract(CanonicalBase):
    vaccine: Optional[str] = None
    district_id: Optional[str] = None
    doses_target: Optional[int] = 0
    doses_administered: Optional[int] = 0
    coverage_pct: Optional[float] = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None


class MedicineStockContract(CanonicalBase):
    district_id: Optional[str] = None
    medicine: Optional[str] = None
    stock_on_hand: Optional[int] = 0
    monthly_consumption: Optional[int] = 0
    days_of_stock: Optional[float] = 0


class IndicatorContract(CanonicalBase):
    name: str = Field(min_length=1)
    value: Optional[float] = None
    target: Optional[float] = None
    district_id: Optional[str] = None
    period: Optional[str] = None


class SurveillanceEventContract(CanonicalBase):
    district_id: str
    event_type: Optional[str] = None
    reported_at: Optional[str] = None
    complete: Optional[bool] = False


HOSPITAL_CONTRACTS: dict[str, type[BaseModel]] = {
    "hospitals": HospitalContract,
    "departments": DepartmentContract,
    "wards": WardContract,
    "beds": BedContract,
    "patients": PatientContract,
    "admissions": AdmissionContract,
    "staff": StaffContract,
    "equipment": EquipmentContract,
    "medicine_inventory": MedicineInventoryContract,
}

COMMUNITY_CONTRACTS: dict[str, type[BaseModel]] = {
    "districts": DistrictContract,
    "facilities": FacilityContract,
    "disease_reports": DiseaseCaseContract,
    "outbreaks": OutbreakContract,
    "health_workers": HealthWorkerContract,
    "vaccinations": VaccinationContract,
    "medicine_stock": MedicineStockContract,
    "indicators": IndicatorContract,
    "surveillance_events": SurveillanceEventContract,
}


def get_contract(workspace: str, resource: str) -> Optional[type[BaseModel]]:
    if workspace == "hospital":
        return HOSPITAL_CONTRACTS.get(resource)
    if workspace == "community":
        return COMMUNITY_CONTRACTS.get(resource)
    return None


def validate_record(workspace: str, resource: str, record: dict) -> tuple[Optional[dict], Optional[str]]:
    """Return (canonical_dict, error). On success error is None."""
    if not isinstance(record, dict):
        return None, f"Invalid record type: {type(record)}"
    if "id" not in record or not record["id"]:
        return None, f"Record missing 'id' field for {resource}"

    contract = get_contract(workspace, resource)
    if contract is None:
        # Unknown resource: minimal check only
        return dict(record), None

    try:
        parsed = contract.model_validate(record)
        return parsed.model_dump(exclude_none=False), None
    except Exception as e:
        return None, str(e)
