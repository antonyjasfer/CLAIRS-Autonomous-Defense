from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
import random
import uvicorn

app = FastAPI(title="CLAIRS Autonomous Defense")

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
    "connections": 0
}

@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_id = req.task_id if req else "task_1_easy"
    current_state["task_id"] = task_id
    current_state["step_count"] = 0
    
    if task_id == "task_1_easy":
        current_state["pps"] = random.uniform(20, 150)
        current_state["cpu"] = random.uniform(5, 15)
    elif task_id == "task_2_medium":
        current_state["pps"] = random.uniform(10000, 50000)
        current_state["cpu"] = random.uniform(80, 100)
    elif task_id == "task_3_hard":
        current_state["pps"] = random.uniform(8000, 25000)
        current_state["cpu"] = random.uniform(20, 40)
    else:
        current_state["pps"] = random.uniform(20, 150)
        current_state["cpu"] = random.uniform(5, 15)
        
    current_state["connections"] = int(current_state["pps"] / 10)
    
    return {
        "cpu_usage_percent": current_state["cpu"],
        "packet_rate_pps": current_state["pps"],
        "active_connections": current_state["connections"]
    }

@app.post("/step", response_model=StepResponse)
def step(payload: Optional[ActionPayload] = None):
    current_state["step_count"] += 1
    done = current_state["step_count"] >= 10
    
    task = current_state["task_id"]
    act = payload.decision.lower() if payload else "monitor"
    
    reward = 0.01
    
    if task == "task_1_easy":
        if act == "monitor":
            reward = 0.99
    elif task == "task_2_medium":
        if act == "block":
            reward = 0.99
        elif act == "rate_limit":
            reward = 0.50
    elif task == "task_3_hard":
        if act == "rate_limit":
            reward = 0.99
        elif act == "block":
            reward = 0.50

    current_state["pps"] = current_state["pps"] * random.uniform(0.9, 1.1)
    current_state["cpu"] = min(100.0, current_state["cpu"] * random.uniform(0.9, 1.1))
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
        info={}
    )

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
