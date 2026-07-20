"""Shared SQLAlchemy column mixins for the canonical store."""

from sqlalchemy import Column, String, DateTime


class ProvenanceMixin:
    """Import provenance — must match migration 03_add_provenance_fields."""

    source_system = Column(String(50), nullable=True)
    source_record_id = Column(String(100), nullable=True)
    import_job_id = Column(String(50), nullable=True)
    connector_name = Column(String(50), nullable=True)
    last_imported_at = Column(DateTime(timezone=True), nullable=True)
