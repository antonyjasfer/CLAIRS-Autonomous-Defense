from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import random
import os
try:
    import joblib
except ImportError:
    pass

from inference import run_threat_analysis

app = FastAPI(title="CLAIRS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

-
@app.get("/")
def serve_dashboard():
    try:
        with open("index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found. Make sure it is uploaded!</h1>", status_code=404)


chaos_states = ["EASY", "MEDIUM", "HARD"]
current_state_idx = 0
state_ticks = 0

@app.get("/scan")
def scan_network(background_tasks: BackgroundTasks):
    global current_state_idx, state_ticks
    
    state_ticks += 1
    if state_ticks > random.randint(5, 15):
        current_state_idx = (current_state_idx + 1) % len(chaos_states)
        state_ticks = 0
        
    difficulty = chaos_states[current_state_idx]
    

    if difficulty == "EASY":
        
        cpu = round(random.uniform(5.0, 20.0), 2)
        pps = random.randint(20, 150)
    elif difficulty == "MEDIUM":
   
        cpu = round(random.uniform(85.0, 99.0), 2)
        pps = random.randint(10000, 50000)
    else: 
      
        cpu = round(random.uniform(15.0, 35.0), 2)
        pps = random.randint(8000, 25000)
        
        background_tasks.add_task(run_threat_analysis, cpu, pps)

    if pps > 5000 and cpu < 40.0:
        diagnosis = "🚨 THREAT | ACTION: IP BLOCKED"
        reward = "+0.40 (Optimal: Attack blocked)"
    elif pps > 5000 and cpu >= 40.0:
        diagnosis = "🚨 THREAT | ACTION: IP BLOCKED"
        reward = "+0.40 (Optimal: Attack blocked)"
    elif pps > 500 and pps <= 5000:
        diagnosis = "⚠️ WARNING | ACTION: RATE LIMITING"
        reward = "+0.30 (Good: Threat contained)"
    else:
        diagnosis = "✅ SAFE | ACTION: MONITORING"
        reward = "+0.40 (Optimal: Allowed user)"

    return {
        "live_metrics": {
            "cpu_usage_percent": cpu,
            "packet_rate_pps": pps
        },
        "difficulty_mode": difficulty,
        "clairs_ai_diagnosis": diagnosis,
        "agent_reward": reward
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
