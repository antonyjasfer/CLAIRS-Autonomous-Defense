# 🛡️ CLAIRS: Autonomous Defense Environment

**A Novel Hybrid Autonomous Defense Framework for IoT Networks**

## 📖 Overview
CLAIRS is not a passive anomaly detection tool. It is an **interactive Reinforcement Learning (RL) environment** where an AI agent learns to autonomously defend vulnerable IoT networks against unpredictable cyberattacks using real-time decision-making and graded rewards.

## 🎯 The Meta OpenEnv Approach
Standard security models passively flag attacks. CLAIRS acts as an autonomous agent operating within a dynamic, chaotic environment. 

### 1. The Environment (State)
The system continuously simulates live IoT telemetry (CPU Load and Packet Rate). 

### 2. The Agent (Actions)
The hybrid AI core continuously evaluates the state and chooses one of three actions in real-time:
* `MONITOR`: Allows normal traffic to pass safely.
* `RATE LIMIT`: Slows down suspicious traffic to protect server health.
* `BLOCK IP`: Drops the connection entirely to stop a critical volumetric attack.

### 3. The Chaos Engine (Difficulty Levels)
The environment actively tries to trick the agent using dynamic difficulty modes:
* **EASY:** Standard Mode (Normal baseline traffic).
* **MEDIUM:** Adaptive Attack (Obvious, massive volumetric DDoS spikes).
* **HARD:** Stealth DDoS (Advanced attacks that keep CPU load low while flooding packet rates, testing the agent's ability to catch zero-day exploits).

### 4. The Graded Reward System
We evaluate the agent using a normalized score from 0 to 1 across Easy, Medium, and Hard scenarios. The agent is graded in real-time based on the consequences of its actions:
* `+0.40`: Optimal Mitigation (Successful Block or Allowed Normal User)
* `+0.30`: Sub-optimal Mitigation (Attack Slowed)
* `-0.30`: Penalty Applied (False Positive Block)
* `-0.60`: System Overload (Ignored a massive attack)

## 🛠️ Architecture & Tech Stack
* **Simulation Engine:** Custom Python telemetry generator (Synthetic Data Pipeline).
* **Hybrid AI Core:** Neural Network acting as the detection engine.
* **API Microservice:** FastAPI serving a real-time state and action matrix.
* **Frontend Dashboard:** HTML5, JavaScript, and Tailwind CSS for real-time visualization of the RL loop, featuring a live Audit Trail terminal.

## 🚀 How to Run the Environment
1. Clone the repository and install dependencies: `pip install fastapi uvicorn pandas scikit-learn joblib`
2. Start the FastAPI backend: `python3 live_defense.py`
3. Open `index.html` in any web browser and click **Initialize Agent**.
