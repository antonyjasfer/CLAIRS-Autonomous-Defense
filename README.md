# CLAIRS: Autonomous IoT Network Defense

CLAIRS is an autonomous, LLM-driven anomaly detection and mitigation agent designed to sit at the edge of IoT networks. It monitors real-time telemetry (CPU usage, Packets Per Second) and dynamically issues firewall commands (`monitor`, `rate_limit`, `block`) to mitigate volumetric DDoS attacks before they compromise the network.

## Agentic Architecture
Unlike traditional static firewalls, CLAIRS utilizes an **Agentic Context Window**. The agent does not simply react to a single frame of data. It maintains a rolling history of the last 3 telemetry steps, allowing the LLM to analyze temporal trends (e.g., distinguishing between a momentary CPU spike and a sustained, rising DDoS attack) before making a strict classification decision. 

To optimize for raw mitigation speed and low latency during an active attack, we intentionally bypassed heavy Chain-of-Thought (CoT) prompting in favor of strict, single-word output enforcement.

## Evaluation Trade-Offs & Engineering Notes

To ensure absolute stability within the strict automated Phase 1 OpenEnv evaluation constraints, we engineered specific safeguards into the environment backend:

* **Reward Boundary Management:** OpenEnv's automated validation requires that cumulative task scores fall strictly within the `(0, 1)` exclusive range. To guarantee mathematical stability and prevent boundary crashes during evaluation, we implemented standard reinforcement learning reward clamping, bounding the final calculated episode score between `0.01` and `0.99`.
* **Mock Telemetry Data:** For this hackathon MVP, the environment backend simulates traffic fluctuations using randomized generation based on difficulty parameters. This allowed us to rapidly prototype and verify the *LLM decision pipeline*. The architecture is highly modular; hooking this agent up to a true network physics engine (like Mininet) or real PCAP traffic streams requires zero changes to the underlying LLM logic.

## Setup & Execution

### 1. Environment Configuration
Ensure your environment variables are set for the LLM inference. You can configure these in your terminal or a `.env` file:
```bash
export API_BASE_URL="[https://api-inference.huggingface.co/v1/](https://api-inference.huggingface.co/v1/)"
export MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
export HF_TOKEN="your_token_here"
```
### 2.Spin up the FastAPI Environment
Start the local server that acts as the IoT edge device:
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```
### 3. Run the Autonomous Agent
In a separate terminal, execute the inference script to begin the evaluation episodes:
```bash
python inference.py
```
