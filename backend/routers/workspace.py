from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.workspace import workspace_registry
from connectors.registry import connector_registry
from models.sql.import_models import ImportJob, ImportJobStatus

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("")
def list_workspaces():
    return workspace_registry.to_dict()


@router.get("/current")
def current_workspace():
    active = workspace_registry.active
    if not active:
        return {"active": None, "workspace": None}
    return {"active": active.type.value, "workspace": active.to_dict()}


@router.post("/switch")
def switch_workspace(workspace_type: str):
    if workspace_type not in ("hospital", "community"):
        raise HTTPException(status_code=400, detail="Invalid workspace. Choose 'hospital' or 'community'.")
    success = workspace_registry.switch_to(workspace_type)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"active": workspace_type, "workspace": workspace_registry.active.to_dict()}


@router.get("/data-source")
def workspace_data_source(workspace: str = "", db: Session = Depends(get_db)):
    """Return badge type based on import provenance."""
    if workspace and workspace not in ("hospital", "community"):
        raise HTTPException(status_code=400, detail="Invalid workspace")
    result = {}
    targets = [workspace] if workspace else ["hospital", "community"]
    for ws in targets:
        job = db.query(ImportJob).filter(
            ImportJob.workspace == ws,
            ImportJob.connector_name.notin_(["demo", "seed"]),
        ).order_by(ImportJob.completed_at.desc()).first()
        if job:
            result[ws] = {"type": "live_readonly", "label": "Live Read-Only", "icon": "🟢", "connector": job.connector_name, "records": job.records_total}
        else:
            job = db.query(ImportJob).filter(ImportJob.workspace == ws).order_by(ImportJob.completed_at.desc()).first()
            if job:
                result[ws] = {"type": "cached_snapshot", "label": "Cached Snapshot", "icon": "🟡", "connector": job.connector_name, "records": job.records_total}
            else:
                result[ws] = {"type": "synthetic_simulation", "label": "Synthetic Simulation", "icon": "🔵", "connector": None, "records": 0}
    return result if not workspace else result[workspace]


@router.get("/capabilities")
def workspace_capabilities():
    active = workspace_registry.active
    if not active:
        return {"connectors": [], "capabilities": []}
    connectors = connector_registry.get_by_workspace(active.type.value)
    caps = []
    for conn in connectors:
        cap = conn.get_capabilities()
        if cap:
            caps.append({"connector": conn.name, "capabilities": cap.to_dict()})
    return {"workspace": active.type.value, "connectors": caps}
