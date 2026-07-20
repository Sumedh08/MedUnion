from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DiseaseReportResponse(BaseModel):
    id: int
    district: str
    disease: str
    confirmed_cases: int
    suspected_cases: int
    deaths: int
    recovered: int
    reporting_week: str


class CommunityKPIResponse(BaseModel):
    district: str
    kpi_name: str
    value: float
    target: float
    achievement_pct: Optional[float] = None
    period: str


class OutbreakAlert(BaseModel):
    district: str
    disease: str
    risk_level: str
    cases_trend: str
    recommendation: str
