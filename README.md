# 🛡️ CLAIRS: Autonomous Defense Environment (OpenEnv)

**An interactive, hybrid-AI Reinforcement Learning environment designed to simulate real-time DDoS mitigation for resource-constrained IoT systems.**

## 📖 Problem Statement
Low-power IoT devices—such as factory sensors and smart cameras—are highly vulnerable to hijacking due to their limited computational capacity. These compromised devices are often used to form large botnets that launch Distributed Denial-of-Service (DDoS) attacks.

Traditional security solutions are too resource-intensive for these edge devices. Our goal was to design a lightweight, adaptive environment where an autonomous agent can learn to make real-time mitigation decisions without relying on static, offline datasets.

## ⚙️ OpenEnv Integration & Architecture
This project is fully compliant with the **OpenEnv** framework, providing a standardized evaluation pipeline for AI agents. 

We engineered a **Hybrid Architecture** to solve the latency constraints of live cybersecurity:
1. **The Environment (Fast Reflex):** The core simulation continuously generates synthetic network telemetry (CPU usage, Packet Rate). It evaluates agent actions using strict, deterministic thresholds, simulating a sub-5-millisecond response layer.
2. **The Agent (Deep Analysis):** The inference engine utilizes a Large Language Model (via an OpenAI-compatible API) to process the state and reason through the mitigation strategy. 

### 🌪️ The Chaos Engine (Tasks)
The environment dynamically simulates three distinct traffic scenarios:
* **Task 1 (Easy):** Normal Traffic Handling. The agent must monitor without triggering false positives.
* **Task 2 (Medium):** Volumetric DDoS. The agent must detect and block a massive packet flood.
* **Task 3 (Hard):** Stealth DDoS. The agent must detect a highly targeted attack that bypasses standard CPU thresholds.

### 🎯 Reward Framework
The agent is evaluated using a normalized OpenEnv reward structure:
* **1.0** → Correct mitigation (blocking a threat) or correct pass-through (monitoring safe traffic).
* **0.5** → Partial mitigation (rate-limiting a severe threat instead of blocking).
* **0.0** → Incorrect action (false positive block or allowing a threat).

## 🛠️ API & Data Models
The environment exposes the standard OpenEnv endpoints:
* `POST /reset` → Initializes the task and returns the initial state.
* `POST /step` → Accepts an `Action` (monitor, rate_limit, block) and returns the new `Observation` and `Reward`.
* `GET /state` → Returns the current simulation variables.

All inputs and outputs are strictly typed using **Pydantic** to ensure consistent parsing by the automated evaluation pipeline.

## 🚀 Running the Evaluation
To run the automated agent against the environment locally:

```bash
git clone <repo-url>
cd <repo-folder>
pip install fastapi uvicorn pydantic requests openai
