from fastapi import APIRouter
from generators.ambulance_data import AmbulanceDataGenerator

router = APIRouter(prefix="/ambulance", tags=["ambulance"])
generator = AmbulanceDataGenerator()

@router.get("/fleet-status")
async def get_fleet_status():
    return generator.generate_fleet_status()
