from typing import List
from models.schemas import ActionRecommendation
from models.enums import ActionType, RiskLevel, ModuleType

class ActionRecommender:
    def recommend(self, module: ModuleType, risk_level: RiskLevel, details: dict) -> List[ActionRecommendation]:
        recommendations = []
        
        if risk_level == RiskLevel.GREEN:
            return []
            
        if module == ModuleType.VACCINE:
            if risk_level in [RiskLevel.RED, RiskLevel.CRITICAL]:
                recommendations.append(ActionRecommendation(
                    id="REC-001",
                    type=ActionType.REDISTRIBUTION,
                    title="Immediate Redistribution Required",
                    description=f"Move inventory from {details.get('facility_id')} to nearest safe facility within 4 hours.",
                    priority="HIGH",
                    impact_score=90.0
                ))
            if "power_status" in details and details["power_status"] == "UNSTABLE":
                 recommendations.append(ActionRecommendation(
                    id="REC-002",
                    type=ActionType.MAINTENANCE,
                    title="Check Power Backup",
                    description="Generator fuel levels low or voltage fluctuation detected.",
                    priority="MEDIUM",
                    impact_score=60.0
                ))
                
        elif module == ModuleType.MEDICINE:
            if details.get("days_to_stockout", 100) < 5:
                 recommendations.append(ActionRecommendation(
                    id="REC-003",
                    type=ActionType.ESCALATION,
                    title="Emergency Procurement Order",
                    description="Stock critical. Initiate expedited procurement.",
                    priority="HIGH",
                    impact_score=85.0
                ))
        
        return recommendations
