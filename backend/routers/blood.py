from fastapi import APIRouter
from generators.blood_transport_data import BloodTransportDataGenerator

router = APIRouter(prefix="/blood", tags=["blood"])
generator = BloodTransportDataGenerator()

@router.get("/active-transports")
async def get_active_transports():
    return generator.generate_active_transports()
