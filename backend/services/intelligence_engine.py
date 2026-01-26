from .anomaly_detector import AnomalyDetector
from .risk_predictor import RiskPredictor
from .impact_scorer import ImpactScorer
from .action_recommender import ActionRecommender
from models.schemas import RiskScore, RiskLevel, ModuleType

class IntelligenceEngine:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.risk_predictor = RiskPredictor()
        self.impact_scorer = ImpactScorer()
        self.action_recommender = ActionRecommender()
        
    def analyze_facility_risk(self, facility_data: dict) -> RiskScore:
        # Example logic for vaccine facility
        temps = facility_data.get('temperatures', [])
        
        # 1. Anomaly Detection
        is_anomaly, deviation, severity = self.anomaly_detector.detect_temperature_anomaly(temps)
        
        # 2. Risk Prediction
        fail_prob = self.risk_predictor.predict_failure_probability(temps)
        
        # 3. Impact Scoring
        score_val = self.impact_scorer.calculate_score(fail_prob, 1000, "HIGH")
        
        # 4. Final Risk Level Determination
        final_level = self.impact_scorer.determine_severity(score_val)
        
        return RiskScore(
            score=score_val,
            level=final_level,
            trend="UP" if fail_prob > 0.5 else "STABLE",
            factors=["Temp Instability" if is_anomaly else "None"]
        )
