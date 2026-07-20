from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HospitalResponse(BaseModel):
    id: str
    name: str
    type: str
    district: str
    state: str
    latitude: float
    longitude: float
    total_beds: int
    occupied_beds: int
    icu_beds: int
    icu_occupied: int
    emergency_beds: int
    emergency_occupied: int
    staff_count: int
    bed_occupancy_pct: Optional[float] = None
    icu_occupancy_pct: Optional[float] = None


class HospitalDetailResponse(HospitalResponse):
    admissions_trend: Optional[List[dict]] = None
    kpis: Optional[List[dict]] = None


class BedOccupancyResponse(BaseModel):
    hospital_id: str
    ward_type: str
    total: int
    occupied: int
    occupancy_pct: float
    recorded_at: datetime


class AdmissionResponse(BaseModel):
    id: int
    hospital_id: str
    patient_id: str
    admission_date: datetime
    discharge_date: Optional[datetime]
    department: str
    diagnosis: Optional[str]
    length_of_stay_days: Optional[float]
