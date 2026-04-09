# CLAIRS: Autonomous IoT Network Defense

CLAIRS is an autonomous, LLM-driven anomaly detection and mitigation agent designed to sit at the edge of IoT networks. It monitors real-time telemetry (CPU usage, Packets Per Second) and dynamically issues firewall commands (`monitor`, `rate_limit`, `block`) to mitigate volumetric DDoS attacks before they compromise the network.

## 🧠 Agentic Architecture
Unlike traditional static firewalls, CLAIRS utilizes an **Agentic Context Window**. The agent does not simply react to a single frame of data. It maintains a rolling history of the last 3 telemetry steps, allowing the LLM to analyze temporal trends (e.g., distinguishing between a momentary CPU spike and a sustained, rising DDoS attack) before making a strict classification decision. 

To optimize for raw mitigation speed and low latency during an active attack, we intentionally bypassed heavy Chain-of-Thought (CoT) prompting in favor of strict, single-word output enforcement.

## ⚙️ Evaluation Trade-Offs & Engineering Notes

To ensure absolute stability within the strict automated Phase 1 OpenEnv evaluation constraints, we engineered specific safeguards into the environment backend:

* **Reward Shaping & Clamping:** OpenEnv's automated validation throws a boundary crash if a cumulative 10-step episode scores exactly `1.0` or `0.0`. To guarantee mathematical stability during automated testing, we scaled our per-step rewards down by a factor of 10 and implemented a hard safety clamp (max `0.09` per step). In an unconstrained production RL setting, this matrix scales up to standard `0.0 - 1.0` bounds.
* **Mock Telemetry Data:** For this hackathon MVP, the environment backend simulates traffic fluctuations using randomized generation based on difficulty parameters. This allowed us to rapidly prototype and verify the *LLM decision pipeline*. The architecture is highly modular; hooking this agent up to a true network physics engine (like Mininet) or real PCAP traffic streams requires zero changes to the underlying LLM logic.

## 🚀 Setup & Execution

1. Ensure your `.env` contains valid `API_BASE_URL` and `API_KEY` configurations.
2. Spin up the FastAPI environment:
   ```bash
   uvicorn server.app:app --host 0.0.0.0 --port 7860
