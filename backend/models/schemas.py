from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .enums import RiskLevel, ModuleType, ActionType

class RiskScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    level: RiskLevel
    trend: str # "UP", "DOWN", "STABLE"
    factors: List[str]

class Prediction(BaseModel):
    timestamp: datetime
    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    is_anomaly: bool = False

class ActionRecommendation(BaseModel):
    id: str
    type: ActionType
    title: str
    description: str
    priority: str # "HIGH", "MEDIUM", "LOW"
    impact_score: float

class FacilityStatus(BaseModel):
    id: str
    name: str
    type: str # "PHC", "CHC", "DISTRICT_HOSPITAL"
    latitude: float
    longitude: float
    risk_score: RiskScore
    last_updated: datetime
    active_alerts: int
    recommendations: List[ActionRecommendation] = []

class AnomalyEvent(BaseModel):
    id: str
    module: ModuleType
    facility_id: str
    timestamp: datetime
    metric: str
    value: float
    threshold: float
    severity: RiskLevel
    description: str

class DashboardOverview(BaseModel):
    system_health_score: float
    facilities_monitored: int
    active_alerts: int
    failures_prevented_24h: int
    module_status: Dict[str, RiskLevel]
