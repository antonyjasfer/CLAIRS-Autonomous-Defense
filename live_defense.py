from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import joblib
import random
import time
import warnings

warnings.filterwarnings('ignore')

app = FastAPI(title="CLAIRS Autonomous Defense Environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🧠 Booting CLAIRS Hybrid Agentic Core...")
ai_model = joblib.load("clairs_neural_core.pkl")

@app.get("/scan")
def scan_network():
    # --- 1. THE CHAOS ENGINE (Difficulty Levels) ---
    chaos_roll = random.random()
    is_attack = False
    
    if chaos_roll < 0.60:
        difficulty = "🟢 EASY (Normal Traffic)"
        cpu = round(random.uniform(5.0, 15.0), 2)
        pps = round(random.uniform(10.0, 50.0), 2)
    elif chaos_roll < 0.85:
        difficulty = "🟡 MEDIUM (Obvious DDoS)"
        is_attack = True
        cpu = round(random.uniform(85.0, 99.9), 2)
        pps = round(random.uniform(8000.0, 15000.0), 2)
    else:
        difficulty = "🔴 HARD (Stealth Chaos Attack)"
        is_attack = True
        cpu = round(random.uniform(20.0, 35.0), 2) 
        pps = round(random.uniform(12000.0, 20000.0), 2)

    # --- 2. THE AI AGENT DECISION ---
    prediction = ai_model.predict([[cpu, pps]])[0]
    
    # --- 3. THE GRADED REWARD SYSTEM ---
    reward = ""
    action_taken = ""

    if prediction == 0: # Agent chooses to MONITOR
        action_taken = "✅ SAFE | ACTION: MONITORING"
        if not is_attack:
            reward = "+0.4 (Optimal: Allowed user)"
        else:
            reward = "-0.6 (CRITICAL: Ignored attack)"
            
    else: # Agent chooses to ACT (Rate Limit or Block)
        if cpu > 80.0 or pps > 10000:
            action_taken = "🚨 THREAT | ACTION: IP BLOCKED"
            if is_attack:
                reward = "+0.4 (Optimal: Attack blocked)"
            else:
                reward = "-0.3 (Penalty: False block)"
        else:
            action_taken = "⚠️ WARNING | ACTION: RATE LIMITED"
            if is_attack:
                reward = "+0.3 (Sub-optimal: Attack slowed)"
            else:
                reward = "-0.2 (Penalty: False limit)"

    return {
        "timestamp": time.time(),
        "live_metrics": {"cpu_usage_percent": cpu, "packet_rate_pps": pps},
        "difficulty_mode": difficulty,
        "clairs_ai_diagnosis": action_taken,
        "agent_reward": reward
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
