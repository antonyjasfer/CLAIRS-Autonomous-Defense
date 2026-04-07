# 🛡️ CLAIRS: Autonomous Defense Environment (OpenEnv)

**An interactive, hybrid-AI Reinforcement Learning environment designed to simulate real-time DDoS mitigation for resource-constrained IoT systems.**

---

## 📖 Problem Statement
Low-power IoT devices—such as factory sensors and smart cameras—are highly vulnerable to hijacking due to their limited computational capacity. These compromised devices are often used to form large botnets that launch Distributed Denial-of-Service (DDoS) attacks.

Traditional security solutions are too resource-intensive for these edge devices. Our goal was to design a lightweight, adaptive environment where an autonomous agent can learn to make real-time mitigation decisions without relying on static, offline datasets.

---

## ⚙️ OpenEnv Integration & Architecture
This project is fully compliant with the **OpenEnv** framework, providing a standardized evaluation pipeline for AI agents. 

We engineered a **Hybrid Architecture** to solve the latency constraints of live cybersecurity:

### ⚡ The Environment (Fast Reflex)
- Continuously generates synthetic network telemetry (CPU usage, packet rate).
- Evaluates agent actions using strict, deterministic thresholds.
- Simulates a sub-5 millisecond response layer.

### 🧠 The Agent (Deep Analysis)
- The inference engine leverages a Large Language Model (via an OpenAI-compatible API).
- Processes environment state and reasons about the optimal mitigation strategy.
- Provides intelligent decision-making aligned with specific task objectives.

---

## 🌪️ The Chaos Engine (Tasks)
The environment dynamically simulates three distinct traffic scenarios:
* **Task 1 (Easy):** Normal Traffic Handling — The agent must monitor safe traffic without triggering false positives.
* **Task 2 (Medium):** Volumetric DDoS — The agent must detect and block a massive packet flood (PPS > 5000).
* **Task 3 (Hard):** Stealth DDoS — The agent must detect a highly targeted attack that bypasses standard CPU thresholds and apply precision rate-limiting.

---

## 🎯 Reward Framework
The agent is evaluated using a strictly normalized OpenEnv reward structure:
* **1.0** → Correct mitigation (blocking a severe threat) or correct pass-through (monitoring safe traffic).
* **0.5** → Partial mitigation (e.g., rate-limiting instead of fully blocking a severe threat).
* **0.0** → Incorrect action (false positive block or allowing a threat).

*Note: The system is optimized to balance security and service continuity, strictly adhering to the 0.0–1.0 bounds.*

---

## 🛠️ API & Data Models
The environment exposes the standard OpenEnv endpoints:
* `POST /reset` → Initializes the specific task ID and returns the initial state.
* `POST /step` → Accepts an `Action` (monitor, rate_limit, block) and returns the new `Observation` and `Reward`.
* `GET /state` → Returns the current simulation variables.

At each timestep, the agent observes the environment state, selects an action, and receives a reward, forming a continuous reinforcement learning loop. All inputs and outputs are strictly typed using **Pydantic** to ensure consistent parsing by the automated evaluation pipeline.

---

## 🚀 Running the Evaluation

### Option A: Running with Docker (Recommended for OpenEnv Evaluation)
To build and run the OpenEnv environment locally using Docker:
```bash
docker build -t clairs .
docker run -p 7860:7860 clairs

git clone https://github.com/antonyjasfer/CLAIRS-Autonomous-Defense.git
cd CLAIRS-Autonomous-Defense
pip install fastapi uvicorn pydantic requests openai
uvicorn live_defense:app --host 0.0.0.0 --port 7860
