# 🛡️ CLAIRS: Autonomous Defense Environment (OpenEnv)

**An interactive, hybrid-AI Reinforcement Learning environment designed to simulate real-time DDoS mitigation for resource-constrained IoT systems.**

---

## 📖 Problem Statement
Low-power IoT devices—such as factory sensors and smart cameras—are highly vulnerable to hijacking due to their limited computational capacity. These compromised devices are often used to form large botnets that launch Distributed Denial-of-Service (DDoS) attacks.

Traditional security solutions are too resource-intensive for these edge devices. Our goal was to design a system that is both lightweight and adaptive, while supporting real-time decision-making.

---

## ⚙️ OpenEnv Integration & Architecture
This project is fully compliant with the **OpenEnv** framework, providing a standardized evaluation pipeline for AI agents.

We engineered a **Hybrid Architecture** to solve the latency constraints of live cybersecurity:

### ⚡ The Environment (Fast Reflex)
- Continuously generates synthetic network telemetry (CPU usage, packet rate)
- Evaluates agent actions using deterministic thresholds
- Simulates a sub-5 millisecond response layer

### 🧠 The Agent (Deep Analysis)
- The inference engine leverages a Large Language Model (via an OpenAI-compatible API)
- Processes environment state and reasons about mitigation strategy
- Provides intelligent decision-making aligned with task objectives

---

## 🌪️ The Chaos Engine (Tasks)
The environment dynamically simulates three distinct traffic scenarios:

- **Task 1 (Easy):** Normal Traffic Handling — agent must monitor without false positives  
- **Task 2 (Medium):** Volumetric DDoS — agent must detect and block high packet flood  
- **Task 3 (Hard):** Stealth DDoS — agent must detect subtle attack patterns with low CPU usage  

---

## 🎯 Reward Framework
The agent is evaluated using a normalized OpenEnv reward structure:

- **1.0** → Correct mitigation or correct pass-through  
- **0.5** → Partial mitigation (rate limiting instead of blocking)  
- **0.0** → Incorrect action (false positive or missed attack)  

The system is optimized to balance **security and service continuity**.

---

## 🛠️ API & Data Models
The environment exposes the standard OpenEnv endpoints:

- `POST /reset` → Initialize task and return initial state  
- `POST /step` → Accept action and return observation + reward  
- `GET /state` → Return current environment state  

At each timestep, the agent observes the environment state, selects an action, and receives a reward, forming a continuous reinforcement learning loop.

All inputs and outputs are strictly typed using **Pydantic** to ensure reliable parsing by the automated evaluation system.

---

## 🚀 Running the Evaluation

```bash
git clone <repo-url>
cd <repo-folder>
pip install fastapi uvicorn pydantic requests openai
python3 inference.py

## 💡 Key Contribution

CLAIRS demonstrates how real-time cybersecurity can be modeled as an interactive reinforcement learning environment, combining fast deterministic response with high-level reasoning through hybrid AI design.
