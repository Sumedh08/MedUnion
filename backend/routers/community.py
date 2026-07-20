from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.community import CommunityAlertEngine
from services.community.adapter import CommunityAdapter
from core.database import get_db

router = APIRouter(prefix="/community", tags=["community"])


def _get_engine(db: Session):
    return CommunityAdapter(db)


@router.get("/districts")
def list_districts(db: Session = Depends(get_db)):
    return _get_engine(db).get_districts_enriched()


@router.get("/districts/{district_id}")
def get_district(district_id: str, db: Session = Depends(get_db)):
    result = _get_engine(db).get_district_detail(district_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"District {district_id} not found")
    return result


@router.get("/districts/{district_id}/kpis")
def get_district_kpis(district_id: str, db: Session = Depends(get_db)):
    kpis = _get_engine(db).compute_kpis(district_id)
    if not kpis:
        raise HTTPException(status_code=404, detail=f"District {district_id} not found")
    return kpis[0]


@router.get("/districts/{district_id}/disease-reports")
def get_district_disease_reports(district_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_disease_reports(district_id)


@router.get("/districts/{district_id}/vaccinations")
def get_district_vaccinations(district_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_vaccination_summary(district_id)


@router.get("/districts/{district_id}/medicine-stock")
def get_district_medicine_stock(district_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_medicine_stock(district_id)


@router.get("/districts/{district_id}/health-workers")
def get_district_health_workers(district_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_health_worker_summary(district_id)


@router.get("/disease-reports")
def get_all_disease_reports(db: Session = Depends(get_db)):
    return _get_engine(db).get_disease_reports()


@router.get("/vaccinations")
def get_all_vaccination_summary(db: Session = Depends(get_db)):
    return _get_engine(db).get_vaccination_summary()


@router.get("/outbreaks")
def get_outbreaks(db: Session = Depends(get_db)):
    return _get_engine(db).get_outbreaks()


@router.get("/kpi/summary")
def get_kpi_summary(db: Session = Depends(get_db)):
    return _get_engine(db).get_kpi_summary()


@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    engine = _get_engine(db)
    return CommunityAlertEngine(engine).check_alerts()
