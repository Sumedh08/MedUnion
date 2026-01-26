import numpy as np
from typing import List, Dict, Tuple
from models.enums import RiskLevel, ModuleType

class AnomalyDetector:
    def detect_temperature_anomaly(self, temps: List[float]) -> Tuple[bool, float, RiskLevel]:
        """
        Detects anomalies in temperature readings.
        Returns: (is_anomaly, deviation_magnitude, severity)
        """
        if not temps:
            return False, 0.0, RiskLevel.GREEN
            
        data = np.array(temps)
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return False, 0.0, RiskLevel.GREEN
            
        latest = data[-1]
        z_score = abs(latest - mean) / std
        
        # Thresholds
        if 2.0 <= latest <= 8.0:
            # Within safe range, but check for rapid drift
            if z_score > 3.0:
                return True, z_score, RiskLevel.AMBER
            return False, 0.0, RiskLevel.GREEN
        else:
            # Out of safe range
            return True, z_score, RiskLevel.RED if abs(latest - 5.0) > 5 else RiskLevel.AMBER

    def detect_stock_anomaly(self, consumption_history: List[int], current_stock: int) -> bool:
        """Detect sudden consumption spikes or abnormal stock levels"""
        if not consumption_history:
            return False
            
        avg_consumption = np.mean(consumption_history)
        if current_stock < avg_consumption * 2: # Less than 2 days coverage
            return True
        return False
