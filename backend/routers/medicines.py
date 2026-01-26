from fastapi import APIRouter
from generators.medicine_data import MedicineDataGenerator

router = APIRouter(prefix="/medicines", tags=["medicines"])
generator = MedicineDataGenerator()

@router.get("/inventory")
async def get_inventory_status():
    return generator.generate_stock_levels()
