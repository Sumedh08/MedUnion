"""Import management endpoints.

Triggers, tracks, and inspects workspace imports.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.import_manager import ImportManager, ImportAlreadyRunningError
from services.connector_resolver import ConnectorResolver, SourceUnavailableError
from services.scheduler import ManualImportScheduler

router = APIRouter(prefix="/import", tags=["import"])


def _get_import_manager(db: Session):
    return ImportManager(db)


@router.post("/{workspace}")
def trigger_import(
    workspace: str,
    connector: str = Query(None, description="Preferred connector name"),
    mode: str = Query("full", regex="^(full|incremental)$"),
    db: Session = Depends(get_db),
):
    """Trigger a full workspace import."""
    mgr = _get_import_manager(db)
    try:
        results = mgr.run_import(workspace, connector_name=connector, mode=mode)
    except ImportAlreadyRunningError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except SourceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        "workspace": workspace,
        "connector": results[0].connector_name if results else None,
        "resources": [
            {
                "resource": r.resource,
                "records_processed": r.records_processed,
                "records_failed": r.records_failed,
                "success": r.success,
            }
            for r in results
        ],
        "total_processed": sum(r.records_processed for r in results),
        "total_failed": sum(r.records_failed for r in results),
    }


@router.get("/jobs")
def list_jobs(
    workspace: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    mgr = _get_import_manager(db)
    return [
        {
            "id": j.id,
            "workspace": j.workspace,
            "connector": j.connector_name,
            "status": j.status,
            "records_total": j.records_total,
            "records_failed": j.records_failed,
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in mgr.get_jobs(workspace, limit)
    ]


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    mgr = _get_import_manager(db)
    job = mgr.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Import job {job_id} not found")
    batches = mgr.get_batches(job_id)
    return {
        "id": job.id,
        "workspace": job.workspace,
        "connector": job.connector_name,
        "mode": job.mode,
        "status": job.status,
        "records_total": job.records_total,
        "records_failed": job.records_failed,
        "errors": job.errors,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "batches": [
            {
                "resource": b.resource,
                "status": b.status,
                "records_inserted": b.records_inserted,
                "records_failed": b.records_failed,
                "error": b.error_message,
                "started_at": b.started_at.isoformat() if b.started_at else None,
                "completed_at": b.completed_at.isoformat() if b.completed_at else None,
            }
            for b in batches
        ],
    }


@router.get("/schedules")
def list_schedules():
    scheduler = ManualImportScheduler()
    return scheduler.list_schedules()


@router.post("/schedules")
def create_schedule(workspace: str, cron_expr: str):
    scheduler = ManualImportScheduler()
    schedule_id = scheduler.schedule(workspace, cron_expr)
    return {"schedule_id": schedule_id, "workspace": workspace, "cron": cron_expr}


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str):
    scheduler = ManualImportScheduler()
    scheduler.cancel(schedule_id)
    return {"status": "cancelled", "schedule_id": schedule_id}
