from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from core.database import Base
import enum


class ImportJobStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportBatchStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String(50), primary_key=True)
    workspace = Column(String(50), nullable=False, index=True)
    connector_name = Column(String(50), nullable=False)
    mode = Column(String(20), default="full")
    status = Column(String(20), default=ImportJobStatus.RUNNING.value)
    records_total = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(String(50), primary_key=True)
    job_id = Column(String(50), ForeignKey("import_jobs.id"), nullable=False, index=True)
    resource = Column(String(100), nullable=False)
    status = Column(String(20), default=ImportBatchStatus.RUNNING.value)
    records_attempted = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ConnectorRun(Base):
    __tablename__ = "connector_runs"

    id = Column(String(50), primary_key=True)
    connector_name = Column(String(50), nullable=False, index=True)
    resource = Column(String(100), nullable=False)
    records_fetched = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    success = Column(Integer, default=1)
    error = Column(Text, nullable=True)
    ran_at = Column(DateTime(timezone=True), server_default=func.now())


class ETLLog(Base):
    __tablename__ = "etl_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), ForeignKey("import_jobs.id"), nullable=True, index=True)
    batch_id = Column(String(50), ForeignKey("import_batches.id"), nullable=True)
    level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QuarantineRecord(Base):
    """Rejected records during import — never enter canonical tables."""

    __tablename__ = "import_quarantine"

    id = Column(String(50), primary_key=True)
    job_id = Column(String(50), ForeignKey("import_jobs.id"), nullable=False, index=True)
    resource = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
