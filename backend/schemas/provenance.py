"""Response metadata for data lineage and AI evidence."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class DataSourceMeta(BaseModel):
    data_source: str = Field(
        description="canonical_db | unavailable | demo_import | synthetic_simulation"
    )
    as_of: Optional[str] = None
    import_job_id: Optional[str] = None
    record_count: Optional[int] = None
    degradation_reason: Optional[str] = None


class EvidenceItem(BaseModel):
    type: str
    metric: str
    value: Any = None
    unit: str = ""
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    status: Optional[str] = None
    benchmark: Optional[float] = None
    source: str = "canonical_db"
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    as_of: Optional[str] = None
    import_job_id: Optional[str] = None
    degradation_reason: Optional[str] = None


class InsufficientData(BaseModel):
    status: str = "insufficient_data"
    message: str
    missing: list[str] = Field(default_factory=list)
    data_source: str = "unavailable"
    confidence: float = 0.0
