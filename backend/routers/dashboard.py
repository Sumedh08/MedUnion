from fastapi import APIRouter
from models.schemas import DashboardOverview, RiskLevel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview():
    return DashboardOverview(
        system_health_score=85.5,
        facilities_monitored=50,
        active_alerts=3,
        failures_prevented_24h=12,
        module_status={
            "VACCINE": RiskLevel.AMBER,
            "MEDICINE": RiskLevel.GREEN,
            "BLOOD": RiskLevel.GREEN,
            "AMBULANCE": RiskLevel.GREEN
        }
    )
