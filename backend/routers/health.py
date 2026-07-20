from fastapi import APIRouter
from connectors.registry import connector_registry

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check():
    return {"status": "healthy", "service": "AI Health Intelligence Platform", "version": "2.0.0"}


@router.get("/connectors")
def connector_health():
    return connector_registry.list()


@router.get("/ping")
def ping():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}
