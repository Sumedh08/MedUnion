"""ETL Pipeline Orchestrator.

Extract → Canonical Map → Validate (contracts) → Load
"""

from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid

from core.logging import logger
from core.events import EventBus, ImportEvents
from connectors.base.base_connector import ReadOnlyConnector
from etl.mappers import get_mapper
from etl.loaders import get_loader
from etl.contracts import validate_record
from models.sql.import_models import QuarantineRecord


@dataclass
class ETLResult:
    success: bool
    connector_name: str
    resource: str
    records_processed: int
    records_failed: int
    records_quarantined: int = 0
    errors: list[str] = field(default_factory=list)
    import_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ETLPipeline:
    """Orchestrates the ETL process from any ReadOnlyConnector."""

    def __init__(self, db=None, workspace: str = None):
        self._db = db
        self._workspace = workspace
        self._mapper = get_mapper(workspace) if workspace else None
        self._loader_cls = get_loader(workspace) if workspace else None

    def run(
        self,
        connector: ReadOnlyConnector,
        resource: str,
        params: Optional[dict] = None,
        import_job_id: Optional[str] = None,
    ) -> ETLResult:
        result = ETLResult(
            success=False,
            connector_name=connector.name,
            resource=resource,
            records_processed=0,
            records_failed=0,
            import_id=import_job_id or str(uuid.uuid4())[:8],
            started_at=datetime.now(timezone.utc),
        )

        try:
            logger.info(f"ETL: Extracting {resource} from {connector.name}")
            raw_data = connector.fetch(resource, params)

            if not raw_data:
                logger.info(f"ETL: No data extracted for {resource}")
                result.success = True
                result.completed_at = datetime.now(timezone.utc)
                return result

            logger.info(f"ETL: Extracted {len(raw_data)} records from {connector.name}/{resource}")

            canonical = raw_data
            if self._mapper:
                # Support FHIR-style resource names via mapper methods
                canonical = self._mapper.map(resource, raw_data)

            validated = []
            for i, record in enumerate(canonical):
                try:
                    clean, err = validate_record(self._workspace or "", resource, record)
                    if err:
                        raise ValueError(err)
                    clean["_source_timestamp"] = datetime.now(timezone.utc).isoformat()
                    clean["_schema_version"] = "1.0.0"
                    # Strip internal-only keys before load
                    for k in list(clean.keys()):
                        if k.startswith("_") and k not in ("_source_timestamp", "_schema_version"):
                            pass
                    validated.append(clean)
                except Exception as e:
                    result.records_failed += 1
                    result.records_quarantined += 1
                    msg = f"Record {i}: {e}"
                    result.errors.append(msg)
                    self._quarantine(import_job_id, resource, record, msg)

            result.records_processed = len(validated)

            if self._loader_cls and self._db and validated:
                try:
                    loader = self._loader_cls(self._db)
                    # Drop ephemeral keys not on models
                    loadable = []
                    for r in validated:
                        row = {k: v for k, v in r.items() if not k.startswith("_")}
                        loadable.append(row)
                    inserted, failed = loader.load(
                        resource, loadable, result.import_id,
                        connector.name, connector.name,
                    )
                    logger.info(f"ETL: Loaded {inserted} {resource} records into DB")
                    if failed:
                        result.records_failed += failed
                except Exception as e:
                    logger.error(f"ETL: Load failed for {resource}: {e}")
                    result.errors.append(f"Load failed: {e}")
                    result.records_failed += len(validated)
                    result.records_processed = 0

            result.success = result.records_failed == 0
            result.completed_at = datetime.now(timezone.utc)

            event = ImportEvents.BATCH_COMPLETED if result.success else ImportEvents.BATCH_FAILED
            EventBus.publish(
                event,
                connector=connector.name,
                resource=resource,
                import_id=result.import_id,
                records_processed=result.records_processed,
                records_failed=result.records_failed,
            )

            logger.info(
                f"ETL: {connector.name}/{resource} — "
                f"{result.records_processed} ok, {result.records_failed} failed, "
                f"{result.records_quarantined} quarantined"
            )

        except Exception as e:
            result.errors.append(str(e))
            result.completed_at = datetime.now(timezone.utc)
            logger.error(f"ETL: {connector.name}/{resource} failed: {e}")

        return result

    def _quarantine(self, job_id: Optional[str], resource: str, record, error: str):
        if not self._db or not job_id:
            return
        try:
            qid = f"q-{uuid.uuid4().hex[:16]}"
            payload = record if isinstance(record, dict) else {"raw": str(record)}
            self._db.add(QuarantineRecord(
                id=qid,
                job_id=job_id,
                resource=resource,
                payload=payload,
                error_message=error[:2000] if error else None,
            ))
            self._db.flush()
        except Exception as e:
            logger.warning(f"ETL: quarantine write failed: {e}")


def import_workspace(db, connector: ReadOnlyConnector, workspace: str, import_job_id: str) -> list[ETLResult]:
    pipeline = ETLPipeline(db=db, workspace=workspace)
    loader_cls = get_loader(workspace)
    if not loader_cls:
        logger.error(f"No loader for workspace: {workspace}")
        return []

    loader = loader_cls(db)
    resource_order = loader.get_resource_order()
    results = []

    logger.info(f"Importing {workspace} workspace from {connector.name}: {len(resource_order)} resources")

    for resource in resource_order:
        result = pipeline.run(connector, resource, import_job_id=import_job_id)
        results.append(result)

    total = sum(r.records_processed for r in results)
    failed = sum(r.records_failed for r in results)
    logger.info(f"Import {workspace} complete: {total} records, {failed} failed")
    return results
