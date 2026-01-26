from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
async def get_all_alerts():
    return [
        {"id": "ALT-001", "module": "VACCINE", "severity": "RED", "message": "Temp excursion at FAC-005", "timestamp": "2026-01-20T10:00:00"},
        {"id": "ALT-002", "module": "AMBULANCE", "severity": "AMBER", "message": "High surge risk in North Zone", "timestamp": "2026-01-20T10:15:00"},
    ]
