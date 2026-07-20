"""EventBus handlers for import lifecycle logging."""

from core.logging import logger
from core.events import EventBus, ImportEvents


def _on_import_started(**data):
    logger.info(f"[Import] Started: workspace={data.get('workspace')}, connector={data.get('connector')}, job={data.get('job_id')}")


def _on_import_completed(**data):
    logger.info(f"[Import] Completed: workspace={data.get('workspace')}, records={data.get('records')}")


def _on_import_failed(**data):
    logger.error(f"[Import] Failed: workspace={data.get('workspace')}, errors={data.get('errors')}")


def _on_batch_started(**data):
    logger.info(f"[Import] Batch started: resource={data.get('resource')}, connector={data.get('connector')}")


def _on_batch_completed(**data):
    logger.info(f"[Import] Batch completed: resource={data.get('resource')}, records={data.get('records_processed')}")


def _on_batch_failed(**data):
    logger.warning(f"[Import] Batch failed: resource={data.get('resource')}, errors={data.get('errors')}")


def register_import_handlers():
    EventBus.subscribe(ImportEvents.IMPORT_STARTED, _on_import_started)
    EventBus.subscribe(ImportEvents.IMPORT_COMPLETED, _on_import_completed)
    EventBus.subscribe(ImportEvents.IMPORT_FAILED, _on_import_failed)
    EventBus.subscribe(ImportEvents.BATCH_STARTED, _on_batch_started)
    EventBus.subscribe(ImportEvents.BATCH_COMPLETED, _on_batch_completed)
    EventBus.subscribe(ImportEvents.BATCH_FAILED, _on_batch_failed)
