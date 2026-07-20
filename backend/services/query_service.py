"""Application query services — sole read path for routers and AI.

ADR-001/002: PostgreSQL is system of record. Connectors are never used here.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from services.hospital.adapter import HospitalAdapter
from services.community.adapter import CommunityAdapter
from models.hospital.organization import Hospital
from models.community.geography import District
from models.sql.import_models import ImportJob, ImportJobStatus


class QueryService:
    """Facade over workspace adapters with provenance metadata."""

    def __init__(self, db: Session):
        self._db = db
        self.hospital = HospitalAdapter(db)
        self.community = CommunityAdapter(db)

    def has_hospital_data(self) -> bool:
        return self._db.query(Hospital).count() > 0

    def has_community_data(self) -> bool:
        return self._db.query(District).count() > 0

    def latest_import(self, workspace: str) -> Optional[ImportJob]:
        return (
            self._db.query(ImportJob)
            .filter(
                ImportJob.workspace == workspace,
                ImportJob.status == ImportJobStatus.COMPLETED.value,
            )
            .order_by(ImportJob.completed_at.desc())
            .first()
        )

    def source_meta(self, workspace: str, record_count: Optional[int] = None) -> dict:
        has = self.has_hospital_data() if workspace == "hospital" else self.has_community_data()
        if not has:
            return {
                "data_source": "unavailable",
                "as_of": None,
                "import_job_id": None,
                "record_count": 0,
                "degradation_reason": "no_canonical_data",
            }
        job = self.latest_import(workspace)
        return {
            "data_source": "canonical_db",
            "as_of": (job.completed_at or job.started_at).isoformat() if job and (job.completed_at or job.started_at) else datetime.now(timezone.utc).isoformat(),
            "import_job_id": job.id if job else None,
            "record_count": record_count,
            "degradation_reason": None,
        }

    def wrap(self, workspace: str, payload: Any, record_count: Optional[int] = None) -> dict:
        """Attach provenance envelope when returning structured payloads."""
        meta = self.source_meta(workspace, record_count)
        if isinstance(payload, list):
            return {"items": payload, **meta, "record_count": record_count if record_count is not None else len(payload)}
        if isinstance(payload, dict):
            return {**payload, **meta}
        return {"data": payload, **meta}
