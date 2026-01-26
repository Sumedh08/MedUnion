from models.enums import RiskLevel

class ImpactScorer:
    def calculate_score(self, risk_prob: float, volume: int, population_risk: str) -> float:
        """
        Calculate impact score (0-100).
        Factors: Probability of failure, Volume of assets, Population vulnerability
        """
        # Base score from probability
        score = risk_prob * 30
        
        # Volume multiplier
        vol_score = min(volume / 1000, 1.0) * 30
        
        # Population multiplier
        pop_multiplier = 1.5 if population_risk == "HIGH" else 1.0
        
        total = (score + vol_score) * pop_multiplier
        return min(total, 99.9)

    def determine_severity(self, score: float) -> RiskLevel:
        if score > 80:
            return RiskLevel.CRITICAL
        elif score > 60:
            return RiskLevel.RED
        elif score > 40:
            return RiskLevel.AMBER
        else:
            return RiskLevel.GREEN
