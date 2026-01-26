import random
from datetime import datetime, timedelta
from typing import List, Dict

class BloodTransportDataGenerator:
    def __init__(self):
        self.routes = [
            ("Central Blood Bank", "District Hospital A"),
            ("Red Cross Center", "City General Hospital"),
            ("Airport Hub", "Super Specialty Center"),
        ]
        
    def generate_active_transports(self) -> List[Dict]:
        transports = []
        for i in range(5): # 5 active transports
            start, end = random.choice(self.routes)
            start_time = datetime.now() - timedelta(minutes=random.randint(0, 120))
            
            # Risk injection
            is_delayed = random.choice([True, False, False])
            
            transports.append({
                "transport_id": f"TR-{random.randint(1000, 9999)}",
                "type": random.choice(["Blood", "Organ", "Plasma"]),
                "source": start,
                "destination": end,
                "start_time": start_time,
                "eta": start_time + timedelta(minutes=180),
                "current_location": {"lat": 12.9716 + random.uniform(-0.1, 0.1), "lng": 77.5946 + random.uniform(-0.1, 0.1)},
                "temperature": 4.0 + (random.uniform(0, 4) if is_delayed else random.uniform(-0.5, 0.5)),
                "traffic_status": "HEAVY" if is_delayed else "NORMAL"
            })
        return transports
