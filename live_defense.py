from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import random
import os
from models import Observation, Action

app = FastAPI(title="clairs-network-defense")

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

current_state = {
    "cpu": 0.0,
    "pps": 0,
    "connections": 0,
    "task_mode": "task_1_easy",
    "steps": 0
}

def generate_telemetry(task_mode: str):
    if task_mode == "task_1_easy":
        cpu = round(random.uniform(5.0, 20.0), 2)
        pps = random.randint(20, 150)
    elif task_mode == "task_2_medium":
        cpu = round(random.uniform(85.0, 99.0), 2)
        pps = random.randint(10000, 50000)
    else:
        cpu = round(random.uniform(15.0, 35.0), 2)
        pps = random.randint(8000, 25000)
        
    connections = pps // 10
    return cpu, pps, connections

@app.post("/reset")
def reset_environment(payload: Optional[Dict[str, Any]] = None):
    task_id = payload.get("task_id") if payload else None
    
    current_state["task_mode"] = task_id or os.getenv("TASK_NAME", random.choice([
        "task_1_easy", "task_2_medium", "task_3_hard"
    ]))
    current_state["steps"] = 0
    
    cpu, pps, connections = generate_telemetry(current_state["task_mode"])
    current_state["cpu"] = cpu
    current_state["pps"] = pps
    current_state["connections"] = connections
    
    return {
        "observation": {
            "cpu_usage_percent": cpu,
            "packet_rate_pps": pps,
            "active_connections": connections
        }
    }

@app.post("/step", response_model=StepResponse)
def step_environment(action: Action):
    current_state["steps"] += 1
    done = current_state["steps"] >= 10
    reward = 0.0
    
    # Task 3 (Hard) Logic: Stealth DDoS requires Rate Limit, Block is penalized
    if current_state["task_mode"] == "task_3_hard":
        if current_state["pps"] > 5000:
            if action.decision == "rate_limit":
                reward = 1.0
            elif action.decision == "block":
                reward = 0.5
            else:
                reward = 0.0
        else:
            if action.decision == "monitor":
                reward = 1.0
            else:
                reward = 0.0
                
    # Task 1 & 2 Logic: Standard Volumetric Defense
    else:
        if current_state["pps"] > 5000:
            if action.decision == "block":
                reward = 1.0
            elif action.decision == "rate_limit":
                reward = 0.5
            else:
                reward = 0.0
        elif current_state["pps"] > 500:
            if action.decision == "rate_limit":
                reward = 1.0
            elif action.decision == "block":
                reward = 0.5
            else:
                reward = 0.0
        else:
            if action.decision == "monitor":
                reward = 1.0
            else:
                reward = 0.0
            
    cpu, pps, connections = generate_telemetry(current_state["task_mode"])
    current_state["cpu"] = cpu
    current_state["pps"] = pps
    current_state["connections"] = connections
    
    return StepResponse(
        observation=Observation(
            cpu_usage_percent=cpu,
            packet_rate_pps=pps,
            active_connections=connections
        ),
        reward=reward,
        done=done,
        info={"task": current_state["task_mode"]}
    )

@app.get("/state")
def get_current_state():
    return current_state
