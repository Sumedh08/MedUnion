import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from models.schemas import Prediction

class RiskPredictor:
    def predict_failure_probability(self, historical_data: List[float], horizon_hours: int = 24) -> float:
        """
        Predict probability of failure within horizon.
        Uses simple linear trend extrapolation for demo.
        """
        if len(historical_data) < 5:
            return 0.1
            
        # Fit linear trend: y = mx + c
        x = np.arange(len(historical_data))
        y = np.array(historical_data)
        m, c = np.polyfit(x, y, 1)
        
        # Extrapolate
        future_x = len(historical_data) + horizon_hours
        predicted_temp = m * future_x + c
        
        # Calculate probability based on distance from safe zone (2-8 C)
        if 2.0 <= predicted_temp <= 8.0:
            return 0.1 + (0.2 if abs(predicted_temp - 5.0) > 2 else 0)
        else:
            dist = min(abs(predicted_temp - 2.0), abs(predicted_temp - 8.0))
            prob = 0.5 + (0.1 * dist)
            return min(prob, 0.99)
            
    def get_predictions(self, historical_data: List[float], start_time: datetime) -> List[Prediction]:
        predictions = []
        if len(historical_data) < 2:
            return predictions
            
        x = np.arange(len(historical_data))
        y = np.array(historical_data)
        m, c = np.polyfit(x, y, 1)
        
        std_err = np.std(y - (m * x + c))
        
        for i in range(1, 14): # Next 12 hours + 1
            future_val = m * (len(historical_data) + i) + c
            pred_time = start_time + timedelta(hours=i)
            
            predictions.append(Prediction(
                timestamp=pred_time,
                predicted_value=future_val,
                confidence_interval_lower=future_val - 1.96 * std_err,
                confidence_interval_upper=future_val + 1.96 * std_err,
                is_anomaly=not (2.0 <= future_val <= 8.0)
            ))
        return predictions
