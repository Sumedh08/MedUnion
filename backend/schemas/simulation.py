from pydantic import BaseModel
from typing import Optional, List, Any


class SimulationScenario(BaseModel):
    id: str
    name: str
    description: str
    parameters: dict
    status: str = "draft"


class SimulationInput(BaseModel):
    scenario_name: str
    parameters: dict


class SimulationOutput(BaseModel):
    scenario_id: str
    scenario_name: str
    impacted_kpis: List[dict]
    forecasts: List[dict]
    capacity_impacts: List[dict]
    recommended_actions: List[str]
    risk_score: float
    data_source: str = "synthetic_simulation"
