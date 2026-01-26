import random
from datetime import datetime
from typing import List, Dict

class AmbulanceDataGenerator:
    def __init__(self):
        self.zones = ["North Zone", "South Zone", "East Zone", "West Zone", "Central"]
        
    def generate_fleet_status(self) -> List[Dict]:
        status_list = []
        for zone in self.zones:
            total = random.randint(10, 20)
            busy = random.randint(0, total)
            
            # Surge condition
            is_surge = busy / total > 0.8
            
            status_list.append({
                "zone": zone,
                "total_ambulances": total,
                "available": total - busy,
                "busy": busy,
                "avg_response_time": random.randint(8, 25), # minutes
                "surge_risk": "HIGH" if is_surge else "LOW"
            })
        return status_list
