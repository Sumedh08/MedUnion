from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class DataSourceBadge(BaseModel):
    type: str  # live_readonly, cached_snapshot, synthetic_simulation
    label: str
    icon: str
    color: str


class KPIResponse(BaseModel):
    id: str
    name: str
    value: Any
    unit: str
    trend: Optional[str] = None
    trend_value: Optional[str] = None
    data_source: DataSourceBadge
    benchmark: Optional[float] = None
    description: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int


class ErrorResponse(BaseModel):
    detail: str
    code: str
    timestamp: str
