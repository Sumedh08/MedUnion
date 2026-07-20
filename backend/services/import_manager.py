"""ImportManager — orchestrates workspace imports end-to-end.

ADR-005: Full import is replace-per-workspace (truncate + load in one transaction).
"""

from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from core.logging import logger
from core.events import EventBus, ImportEvents
from services.connector_resolver import ConnectorResolver, MapperRequiredError
from etl.pipeline import ETLPipeline, ETLResult
from models.sql.import_models import ImportJob, ImportJobStatus, ImportBatch, ImportBatchStatus
from etl.loaders import get_loader


class ImportAlreadyRunningError(Exception):
    pass


# Truncate order: children first (FK-safe reverse of load order where possible)
HOSPITAL_TRUNCATE_ORDER = [
    "admissions", "inventory", "equipment", "staff", "beds", "wards",
    "departments", "patients", "hospitals",
]
COMMUNITY_TRUNCATE_ORDER = [
    "surveillance_events", "indicators", "medicine_stock", "vaccinations",
    "health_workers", "outbreaks", "disease_cases", "facilities", "districts",
]


class ImportManager:
    """Multi-workspace import orchestrator with job tracking."""

    def __init__(self, db: Session, resolver: Optional[ConnectorResolver] = None):
        self._db = db
        self._resolver = resolver or ConnectorResolver()

    def _resolve_connector(self, workspace: str, preferred: Optional[str]):
        return self._resolver.resolve(workspace, preferred=preferred)

    def start_import(
        self,
        workspace: str,
        connector_name: Optional[str] = None,
        mode: str = "full",
    ):

        running = (
            self._db.query(ImportJob)
            .filter(
                ImportJob.workspace == workspace,
                ImportJob.status == ImportJobStatus.RUNNING.value,
            )
            .first()
        )
        if running:
            raise ImportAlreadyRunningError(
                f"Import already running for workspace '{workspace}' (job {running.id})"
            )

        connector = self._resolve_connector(workspace, connector_name)

        job_id = f"imp-{workspace}-{uuid.uuid4().hex[:12]}"

        job = ImportJob(
            id=job_id,
            workspace=workspace,
            connector_name=connector.name,
            mode=mode,
            status=ImportJobStatus.RUNNING.value,
        )
        self._db.add(job)
        self._db.flush()

        EventBus.publish(
            ImportEvents.IMPORT_STARTED,
            job_id=job_id,
            workspace=workspace,
            connector=connector.name,
        )

        return job, connector



    def run_import(
        self,
        workspace: str,
        connector_name: Optional[str] = None,
        mode: str = "full",
    ) -> list[ETLResult]:
        job, connector = self.start_import(workspace, connector_name, mode)

        loader_cls = get_loader(workspace)
        resource_order = loader_cls(self._db).get_resource_order() if loader_cls else []
        pipeline = ETLPipeline(db=self._db, workspace=workspace)
        results = []
        total_ok = 0
        total_fail = 0
        errors = []

        try:

            for resource in resource_order:
                batch_id = f"batch-{uuid.uuid4().hex}"
                batch = ImportBatch(
                    id=batch_id,
                    job_id=job.id,
                    resource=resource,
                    status=ImportBatchStatus.RUNNING.value,
                )
                self._db.add(batch)
                self._db.flush()

                EventBus.publish(
                    ImportEvents.BATCH_STARTED,
                    job_id=job.id,
                    batch_id=batch_id,
                    resource=resource,
                )

                try:
                    result = pipeline.run(connector, resource, import_job_id=job.id)
                except Exception as e:
                    result = ETLResult(
                        success=False,
                        connector_name=connector.name,
                        resource=resource,
                        records_processed=0,
                        records_failed=0,
                        errors=[str(e)],
                        import_id=job.id,
                        started_at=datetime.now(timezone.utc),
                        completed_at=datetime.now(timezone.utc),
                    )

                batch.records_attempted = result.records_processed + result.records_failed
                batch.records_inserted = result.records_processed
                batch.records_failed = result.records_failed
                batch.status = (
                    ImportBatchStatus.COMPLETED.value if result.success else ImportBatchStatus.FAILED.value
                )
                if result.errors:
                    batch.error_message = "; ".join(result.errors[:5])
                batch.completed_at = datetime.now(timezone.utc)
                self._db.flush()

                if result.success:
                    EventBus.publish(
                        ImportEvents.BATCH_COMPLETED,
                        job_id=job.id,
                        batch_id=batch_id,
                        resource=resource,
                        records=result.records_processed,
                    )
                else:
                    EventBus.publish(
                        ImportEvents.BATCH_FAILED,
                        job_id=job.id,
                        batch_id=batch_id,
                        resource=resource,
                        errors=result.errors,
                    )

                total_ok += result.records_processed
                total_fail += result.records_failed
                if result.errors:
                    errors.extend(result.errors)
                results.append(result)

            job.records_total = total_ok
            job.records_failed = total_fail
            job.errors = errors[:50] if errors else None
            job.status = (
                ImportJobStatus.COMPLETED.value if total_fail == 0 else ImportJobStatus.FAILED.value
            )
            job.completed_at = datetime.now(timezone.utc)
            self._db.flush()

            if job.status == ImportJobStatus.COMPLETED.value:
                EventBus.publish(
                    ImportEvents.IMPORT_COMPLETED,
                    job_id=job.id,
                    workspace=workspace,
                    records=total_ok,
                )
            else:
                EventBus.publish(
                    ImportEvents.IMPORT_FAILED,
                    job_id=job.id,
                    workspace=workspace,
                    errors=errors,
                )

            self._db.commit()
            logger.info(
                f"ImportManager: committed import for '{workspace}' "
                f"({total_ok} records, {total_fail} failed)"
            )

            # Rebuild knowledge graph projection from canonical store
            try:
                from knowledge_graph.graph import rebuild_from_database
                rebuild_from_database(self._db)
            except Exception as e:
                logger.warning(f"KG rebuild after import failed: {e}")

            return results

        except Exception as e:
            self._db.rollback()
            try:
                job.status = ImportJobStatus.FAILED.value
                job.completed_at = datetime.now(timezone.utc)
                job.errors = [str(e)]
                self._db.add(job)
                self._db.commit()
            except Exception:
                self._db.rollback()
            logger.error(f"ImportManager: import for '{workspace}' rolled back and marked FAILED: {e}")
            EventBus.publish(
                ImportEvents.IMPORT_FAILED,
                job_id=job.id,
                workspace=workspace,
                errors=[str(e)],
            )
            raise

    def get_job(self, job_id: str) -> Optional[ImportJob]:
        return self._db.query(ImportJob).filter(ImportJob.id == job_id).first()

    def get_jobs(self, workspace: Optional[str] = None, limit: int = 20) -> list[ImportJob]:
        q = self._db.query(ImportJob)
        if workspace:
            q = q.filter(ImportJob.workspace == workspace)
        return q.order_by(ImportJob.started_at.desc()).limit(limit).all()

    def get_batches(self, job_id: str) -> list[ImportBatch]:
        return (
            self._db.query(ImportBatch)
            .filter(ImportBatch.job_id == job_id)
            .order_by(ImportBatch.started_at)
            .all()
        )
