from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

from simulation.engine import digital_twin

router = APIRouter(prefix="/simulation", tags=["simulation"])


class ScenarioCreate(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None


@router.post("/scenarios")
def create_scenario(req: ScenarioCreate):
    scenario = digital_twin.create_scenario(req.name, req.description, req.parameters)
    return scenario


@router.get("/scenarios")
def list_scenarios():
    return {"scenarios": digital_twin.list_scenarios()}


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    scenarios = digital_twin.list_scenarios()
    for s in scenarios:
        if s["id"] == scenario_id:
            return s
    raise HTTPException(404, "Scenario not found")


@router.post("/run/{scenario_id}")
def run_simulation(scenario_id: str):
    result = digital_twin.run_simulation(scenario_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.get("/result/{scenario_id}")
def get_result(scenario_id: str):
    result = digital_twin.get_simulation_result(scenario_id)
    if not result:
        raise HTTPException(404, "Simulation result not found")
    return result


@router.get("/active")
def active_simulations():
    return {"active": {k: {"scenario_id": k, "simulated_at": v.get("simulated_at")} for k, v in digital_twin.active_simulations.items()}}
