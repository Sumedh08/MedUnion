import random
from datetime import datetime, timedelta
from typing import List, Dict

class MedicineDataGenerator:
    def __init__(self):
        self.medicines = [
            "Paracetamol", "Amoxicillin", "Insulin", "ORS", "Metformin", 
            "Azithromycin", "Ibuprofen", "Ceftriaxone"
        ]
        self.facilities = [f"FAC-{i:03d}" for i in range(1, 21)]

    def generate_stock_levels(self) -> List[Dict]:
        data = []
        for fac in self.facilities:
            for med in self.medicines:
                # Random stock logic
                max_stock = random.randint(500, 2000)
                current = random.randint(0, max_stock)
                
                # Expiry logic
                expiry_date = datetime.now() + timedelta(days=random.randint(10, 365))
                if random.random() < 0.1: # 10% chance of near-expiry
                   expiry_date = datetime.now() + timedelta(days=random.randint(1, 30))
                
                data.append({
                    "facility_id": fac,
                    "medicine_name": med,
                    "stock_current": current,
                    "stock_max": max_stock,
                    "consumption_rate": random.randint(10, 50), # per day
                    "expiry_date": expiry_date
                })
        return data
