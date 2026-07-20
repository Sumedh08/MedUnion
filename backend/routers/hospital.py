from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from services.hospital import AlertEngine
from services.hospital.adapter import HospitalAdapter
from core.database import get_db

router = APIRouter(prefix="/hospital", tags=["hospital"])


def _get_engine(db: Session):
    return HospitalAdapter(db)


@router.get("")
def list_hospitals(db: Session = Depends(get_db)):
    return _get_engine(db).get_hospitals_enriched()


@router.get("/{hospital_id}")
def get_hospital(hospital_id: str, db: Session = Depends(get_db)):
    result = _get_engine(db).get_hospital_detail(hospital_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Hospital {hospital_id} not found")
    return result


@router.get("/{hospital_id}/kpis")
def get_hospital_kpis(hospital_id: str, db: Session = Depends(get_db)):
    kpis = _get_engine(db).compute_kpis(hospital_id)
    if not kpis:
        raise HTTPException(status_code=404, detail=f"Hospital {hospital_id} not found")
    return kpis[0]


@router.get("/{hospital_id}/occupancy")
def get_hospital_occupancy(hospital_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_occupancy_by_ward(hospital_id)


@router.get("/{hospital_id}/admissions")
def get_hospital_admissions(hospital_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return _get_engine(db).get_admissions_trend(hospital_id, days)


@router.get("/{hospital_id}/equipment")
def get_hospital_equipment(hospital_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_equipment_status(hospital_id)


@router.get("/{hospital_id}/staff")
def get_hospital_staff(hospital_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_staff_summary(hospital_id)


@router.get("/{hospital_id}/inventory")
def get_hospital_inventory(hospital_id: str, db: Session = Depends(get_db)):
    return _get_engine(db).get_inventory(hospital_id)


@router.get("/kpi/summary")
def get_kpi_summary(db: Session = Depends(get_db)):
    return _get_engine(db).get_kpi_summary()


@router.get("/alerts/all")
def get_all_alerts(db: Session = Depends(get_db)):
    engine = _get_engine(db)
    return AlertEngine(engine).check_alerts()
