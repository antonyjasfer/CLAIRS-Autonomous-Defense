from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import random
import os
try:
    import joblib
except ImportError:
    pass

# NEW: Import our LLM Threat Analyzer
from inference import run_threat_analysis

app = FastAPI(title="CLAIRS Backend")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# HUGGING FACE HTML SERVER ROUTE
# ---------------------------------------------------------
@app.get("/")
def serve_dashboard():
    try:
        with open("index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found. Make sure it is uploaded!</h1>", status_code=404)

# ---------------------------------------------------------
# CLAIRS AI CORE & CHAOS ENGINE LOOP
# ---------------------------------------------------------
chaos_states = ["EASY", "MEDIUM", "HARD"]
current_state_idx = 0
state_ticks = 0

# NEW: Added background_tasks so the LLM doesn't freeze our live UI!
@app.get("/scan")
def scan_network(background_tasks: BackgroundTasks):
    global current_state_idx, state_ticks
    
    # 1. Chaos Engine - Rotate difficulty scenarios
    state_ticks += 1
    if state_ticks > random.randint(5, 15):
        current_state_idx = (current_state_idx + 1) % len(chaos_states)
        state_ticks = 0
        
    difficulty = chaos_states[current_state_idx]
    
    # 2. Simulate Network Telemetry based on Difficulty
    if difficulty == "EASY":
        # Normal Traffic
        cpu = round(random.uniform(5.0, 20.0), 2)
        pps = random.randint(20, 150)
    elif difficulty == "MEDIUM":
        # Massive Volumetric DDoS
        cpu = round(random.uniform(85.0, 99.0), 2)
        pps = random.randint(10000, 50000)
    else: 
        # HARD: Stealth Chaos Attack (Low CPU, High Packets)
        cpu = round(random.uniform(15.0, 35.0), 2)
        pps = random.randint(8000, 25000)
        
        # ---> NEW: TRIGGER DEEP LLM ANALYSIS IN THE BACKGROUND <---
        background_tasks.add_task(run_threat_analysis, cpu, pps)

    # 3. AI Agent Decision & Graded Reward Logic
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
    # Runs on port 7860 specifically for Hugging Face compatibility
    uvicorn.run(app, host="0.0.0.0", port=7860)
