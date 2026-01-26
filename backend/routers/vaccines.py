from fastapi import APIRouter
from typing import List
from generators.vaccine_data import VaccineDataGenerator
from services.intelligence_engine import IntelligenceEngine
from models.schemas import FacilityStatus, RiskLevel

router = APIRouter(prefix="/vaccines", tags=["vaccines"])
generator = VaccineDataGenerator()
engine = IntelligenceEngine()

@router.get("/facilities", response_model=List[FacilityStatus])
async def get_vaccine_facilities():
    raw_status = generator.get_facility_status()
    results = []
    
    for fac in raw_status:
        # Simulate getting historical data for analysis
        temps = generator.generate_temperature_readings(fac['id'])['temperature'].tolist()
        
        # Analyze using Intelligence Engine
        risk = engine.analyze_facility_risk({'temperatures': temps})
        
        # Get recommendations
        recs = engine.action_recommender.recommend("VACCINE", risk.level, {'facility_id': fac['id'], 'power_status': fac['power_status']})
        
        results.append(FacilityStatus(
            id=fac['id'],
            name=fac['name'],
            type=fac['type'],
            latitude=fac['lat'],
            longitude=fac['lng'],
            risk_score=risk,
            last_updated=fac['last_updated'],
            active_alerts=1 if risk.level in [RiskLevel.RED, RiskLevel.AMBER] else 0,
            recommendations=recs
        ))
    return results
