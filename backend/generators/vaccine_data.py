import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

class VaccineDataGenerator:
    def __init__(self):
        # Real Chennai & Tiruvallur Facility Data
        self.facilities_meta = [
            {"id": "FAC-CHE-001", "name": "Rajiv Gandhi Govt General Hospital", "lat": 13.0815, "lng": 80.2768, "type": "Medical College"},
            {"id": "FAC-CHE-002", "name": "Stanley Medical College", "lat": 13.1075, "lng": 80.2878, "type": "Medical College"},
            {"id": "FAC-CHE-003", "name": "Kilpauk Medical College", "lat": 13.0789, "lng": 80.2427, "type": "Medical College"},
            {"id": "FAC-CHE-004", "name": "Omandurar Govt Estate Hospital", "lat": 13.0694, "lng": 80.2748, "type": "Super Specialty"},
            {"id": "FAC-CHE-005", "name": "Adyar Cancer Institute", "lat": 13.0067, "lng": 80.2482, "type": "Specialty Center"},
            {"id": "FAC-TRV-001", "name": "Tiruvallur District HQ Hospital", "lat": 13.1416, "lng": 79.9079, "type": "District Hospital"},
            {"id": "FAC-KPM-001", "name": "Kancheepuram District HQ Hospital", "lat": 12.8342, "lng": 79.7036, "type": "District Hospital"},
            {"id": "VAC-STO-001", "name": "TNMSC Central Warehouse (Anna Nagar)", "lat": 13.0850, "lng": 80.2100, "type": "Central Storage"},
            {"id": "UPH-MYL-012", "name": "Mylapore Urban PHC", "lat": 13.0368, "lng": 80.2676, "type": "UPHC"},
            {"id": "UPH-TGR-005", "name": "T. Nagar Urban PHC", "lat": 13.0400, "lng": 80.2300, "type": "UPHC"},
        ]
        
    def generate_temperature_readings(self, facility_id: str, hours: int = 24) -> pd.DataFrame:
        """Generate temperature readings with simulated patterns"""
        timestamps = [datetime.now() - timedelta(hours=i) for i in range(hours)]
        timestamps.reverse()
        
        # Base temperature around 4.0°C (ideal: 2-8°C)
        base_temp = 4.0
        noise = np.random.normal(0, 0.5, hours)
        
        # Add day/night cycle
        cycle = np.sin(np.linspace(0, 2*np.pi, hours)) * 1.5
        
        temps = base_temp + noise + cycle
        
        # Inject anomaly for specific facilities (Simulation of failure)
        # RGGGH and T. Nagar PHC have simulated issues
        if facility_id in ["FAC-CHE-001", "UPH-TGR-005"]:
            # Drift upwards for last 6 hours
            temps[-6:] += np.linspace(0, 5, 6)
            
        return pd.DataFrame({
            "timestamp": timestamps,
            "temperature": temps,
            "facility_id": facility_id
        })

    def get_facility_status(self) -> List[Dict]:
        """Generate status for real Chennai facilities"""
        status_list = []
        for fac in self.facilities_meta:
            # Randomly assign a 'state' affecting risk (Deterministic for demo: RGGGH is risky)
            is_risky = fac['id'] in ["FAC-CHE-001", "UPH-TGR-005"]
            current_temp = 4.0 + (5.0 if is_risky else 0) + np.random.normal(0, 0.5)
            
            status_list.append({
                "id": fac['id'],
                "name": fac['name'], # Include real name
                "type": fac['type'],
                "lat": fac['lat'], # Real lat
                "lng": fac['lng'], # Real lng
                "current_temp": round(current_temp, 2),
                "power_status": "UNSTABLE" if is_risky else "STABLE",
                "last_updated": datetime.now()
            })
        return status_list
