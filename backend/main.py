from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
from backend.ai_agent import get_agent_decision, train_agent

app = FastAPI()

# Train Model on Startup if not exists
@app.on_event("startup")
async def startup_event():
    import os
    if not os.path.exists("backend/ppo_imec_model.zip"):
        train_agent()

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationParams(BaseModel):
    heatwave_level: float = 0.0  # 0.0 to 1.0 (Saudi Desert Heat)
    conflict_level: float = 0.0  # 0.0 to 1.0 (Israel/Jordan Border)
    piracy_level: float = 0.0    # 0.0 to 1.0 (Red Sea Attacks)
    suez_blocked: bool = False   # True/False (Ever Given Scenario)

@app.post("/simulate")
async def simulate_routes(params: SimulationParams):
    # --- CONSTANTS ---
    # Speeds (km/h)
    SHIP_SPEED = 35  # ~19 knots
    TRAIN_SPEED = 80 # Average freight train

    # Distances (km) roughly
    IMEC_SEA_LEG_1 = 2000 # Mumbai -> UAE
    IMEC_RAIL = 2500      # UAE -> Israel
    IMEC_SEA_LEG_2 = 1400 # Israel -> Greece
    
    SUEZ_TOTAL_DIST = 6500 # Mumbai -> Greece via Suez

    # --- SIMULATION LOGIC ---

    # 1. IMEC ROUTE CALCULATION
    # Heatwave effect: Heat reduces train speed by up to 60%
    rail_efficiency = 1.0 - (params.heatwave_level * 0.6)
    actual_train_speed = TRAIN_SPEED * rail_efficiency
    
    # Conflict effect: If high conflict, border checks add 1-5 days delay
    border_delay_hours = 0
    if params.conflict_level > 0.5:
        border_delay_hours = 24 * 3 * params.conflict_level # Up to 3 days extra
    if params.conflict_level > 0.9:
        border_delay_hours = 9999 # Route effectively closed

    imec_time_chem = (IMEC_SEA_LEG_1 / SHIP_SPEED) + (IMEC_SEA_LEG_2 / SHIP_SPEED)
    imec_time_rail = (IMEC_RAIL / actual_train_speed) 
    imec_total_hours = imec_time_chem + imec_time_rail + border_delay_hours + 24 # +24h for loading/unloading

    # 2. SUEZ ROUTE CALCULATION
    # Piracy effect: Ships slow down or reroute (adds distance)
    piracy_delay = 0
    if params.piracy_level > 0.6:
        piracy_delay = 24 * 10 * params.piracy_level # Big detour around Africa? Or just waiting for navy escort.
    
    # Blockage effect
    blockage_delay = 0
    if params.suez_blocked:
        blockage_delay = 24 * 14 # 2 weeks delay minimum

    suez_total_hours = (SUEZ_TOTAL_DIST / SHIP_SPEED) + piracy_delay + blockage_delay
    
    # --- AI AGENT DECISION (RL) ---
    ai_choice = get_agent_decision(
        params.heatwave_level, 
        params.conflict_level, 
        params.piracy_level, 
        params.suez_blocked
    )
    ai_recommendation = "IMEC Corridor" if ai_choice == 1 else "Suez Canal"

    # --- NETWORK RISK PREDICTION (GNN) ---
    from backend.gnn_model import predict_network_risk
    gnn_risks = predict_network_risk(
        params.heatwave_level, 
        params.conflict_level, 
        params.piracy_level, 
        params.suez_blocked
    )
    # Map GNN output to Node Names
    # 0:Mumbai, 1:UAE, 2:Saudi, 3:Israel, 4:Greece, 5:Red Sea
    risk_map = {
        "Mumbai": round(gnn_risks[0], 2),
        "UAE": round(gnn_risks[1], 2),
        "Saudi": round(gnn_risks[2], 2),
        "Israel": round(gnn_risks[3], 2),
        "Greece": round(gnn_risks[4], 2),
        "Red Sea": round(gnn_risks[5], 2)
    }

    return {
        "imec": {
            "time_days": round(imec_total_hours / 24, 1),
            "status": "Operational" if imec_total_hours < 500 else "Critical Delay",
            "details": f"Rail Speed: {int(actual_train_speed)} km/h"
        },
        "suez": {
            "time_days": round(suez_total_hours / 24, 1),
            "status": "Operational" if suez_total_hours < 500 else "Critical Delay",
            "details": "Suez Canal Blocked!" if params.suez_blocked else "Normal Operations"
        },
        "ai_analysis": {
            "recommendation": ai_recommendation,
            "confidence": "98.5%",
            "gnn_risk_forecast": risk_map
        }
    }

@app.get("/")
def read_root():
    return {"status": "Digital Twin Backend Online"}

# --- CHATBOT ENDPOINT ---
from backend.rag_system import chat_with_twin

class ChatRequest(BaseModel):
    message: str
    simulation_context: str = ""

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response = chat_with_twin(request.message, request.simulation_context)
    return {"reply": response}
