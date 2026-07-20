from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ForecastResponse(BaseModel):
    metric: str
    entity_id: str
    entity_name: str
    predicted_values: List[dict]
    confidence_interval_lower: List[float]
    confidence_interval_upper: List[float]
    methodology: str


class AnomalyResponse(BaseModel):
    entity_id: str
    entity_name: str
    metric: str
    current_value: float
    expected_value: float
    deviation_pct: float
    severity: str
    explanation: str


class RecommendationResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    category: str
    entity_id: str
    reasoning: str
    expected_impact: str
    created_at: datetime
    data_source: str = "synthetic_simulation"


class TrendSummary(BaseModel):
    metric: str
    direction: str
    change_pct: float
    period: str
    significance: str
