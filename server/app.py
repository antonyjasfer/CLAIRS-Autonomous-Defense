from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

app = FastAPI(title="CLAIRS Autonomous Defense - Advanced Grader")

class ResetRequest(BaseModel):
    task_id: str = "task_1_easy"

class ActionPayload(BaseModel):
    decision: str = "monitor"

class Observation(BaseModel):
    cpu_usage_percent: float
    packet_rate_pps: float
    active_connections: int

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

current_state = {
    "task_id": "task_1_easy",
    "step_count": 0,
    "cpu": 0.0,
    "pps": 0.0,
    "connections": 0,
    "system_health": 100.0
}

# Deterministic attack trajectories (replaces random.uniform)
TRAJECTORIES = {
    "task_1_easy": [
        {"pps": 100, "cpu": 10.0}, {"pps": 110, "cpu": 11.0}, {"pps": 95, "cpu": 9.5}, 
        {"pps": 105, "cpu": 10.5}, {"pps": 120, "cpu": 12.0}, {"pps": 100, "cpu": 10.0},
        {"pps": 115, "cpu": 11.5}, {"pps": 90, "cpu": 9.0}, {"pps": 105, "cpu": 10.5}, {"pps": 100, "cpu": 10.0}
    ],
    "task_2_medium": [
        {"pps": 200, "cpu": 15.0}, {"pps": 5000, "cpu": 60.0}, {"pps": 15000, "cpu": 85.0}, 
        {"pps": 25000, "cpu": 95.0}, {"pps": 30000, "cpu": 99.0}, {"pps": 35000, "cpu": 99.0},
        {"pps": 40000, "cpu": 99.0}, {"pps": 45000, "cpu": 99.0}, {"pps": 50000, "cpu": 99.0}, {"pps": 50000, "cpu": 99.0}
    ],
    "task_3_hard": [
        {"pps": 150, "cpu": 12.0}, {"pps": 8000, "cpu": 35.0}, {"pps": 8500, "cpu": 38.0}, 
        {"pps": 9000, "cpu": 40.0}, {"pps": 9500, "cpu": 42.0}, {"pps": 15000, "cpu": 55.0},
        {"pps": 20000, "cpu": 65.0}, {"pps": 22000, "cpu": 70.0}, {"pps": 24000, "cpu": 75.0}, {"pps": 25000, "cpu": 80.0}
    ]
}

@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_id = req.task_id if req else "task_1_easy"
    if task_id not in TRAJECTORIES:
        task_id = "task_1_easy"
        
    current_state["task_id"] = task_id
    current_state["step_count"] = 0
    current_state["system_health"] = 100.0
    
    # Load first step of trajectory
    initial_data = TRAJECTORIES[task_id][0]
    current_state["pps"] = initial_data["pps"]
    current_state["cpu"] = initial_data["cpu"]
    current_state["connections"] = int(current_state["pps"] / 10)
    
    return {
        "cpu_usage_percent": current_state["cpu"],
        "packet_rate_pps": current_state["pps"],
        "active_connections": current_state["connections"]
    }

@app.post("/step", response_model=StepResponse)
def step(payload: Optional[ActionPayload] = None):
    task = current_state["task_id"]
    act = payload.decision.lower() if payload else "monitor"
    step_idx = current_state["step_count"]
    
    # Calculate Dynamic Partial Reward based on action impact
    reward = 0.01
    
    if task == "task_1_easy":
        if act == "monitor": reward = 0.99
        elif act == "rate_limit": reward = 0.40 # False positive penalty
        elif act == "block": reward = 0.10      # Severe false positive penalty
            
    elif task == "task_2_medium":
        if step_idx < 1: # Traffic is normal
            reward = 0.99 if act == "monitor" else 0.20
        else: # Volumetric attack active
            if act == "block": reward = 0.99
            elif act == "rate_limit": reward = 0.60 # Partial mitigation
            elif act == "monitor": reward = 0.01    # Complete failure
                
    elif task == "task_3_hard":
        if step_idx < 1: # Traffic is normal
            reward = 0.99 if act == "monitor" else 0.20
        else: # Stealth attack active
            if act == "rate_limit": reward = 0.99
            elif act == "block": reward = 0.40      # Too aggressive for stealth
            elif act == "monitor": reward = 0.01    # Allowed attack

    # Advance state to the next deterministic step
    current_state["step_count"] += 1
    done = current_state["step_count"] >= 10
    
    next_step_idx = min(current_state["step_count"], 9)
    next_data = TRAJECTORIES[task][next_step_idx]
    
    # Simulate environment reacting to agent's action
    mitigation_factor = 1.0
    if act == "block": mitigation_factor = 0.05
    elif act == "rate_limit": mitigation_factor = 0.40
        
    current_state["pps"] = next_data["pps"] * mitigation_factor
    current_state["cpu"] = min(100.0, next_data["cpu"] * mitigation_factor)
    current_state["connections"] = int(current_state["pps"] / 10)

    obs = Observation(
        cpu_usage_percent=current_state["cpu"],
        packet_rate_pps=current_state["pps"],
        active_connections=current_state["connections"]
    )
    
    return StepResponse(
        observation=obs,
        reward=reward,
        done=done,
        info={"mitigation_applied": act}
    )

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
