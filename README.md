# CLAIRS: Autonomous IoT Network Defense

> An OpenEnv-compliant reinforcement learning environment for training AI agents to defend IoT networks against DDoS attacks in real time.

## Overview

CLAIRS (**C**losed-**L**oop **A**utonomous **I**ncident **R**esponse **S**ystem) is an LLM-driven anomaly detection and mitigation agent designed to sit at the edge of IoT networks. It monitors real-time telemetry (CPU, PPS, bandwidth, memory, system health) and dynamically issues firewall commands (`monitor`, `rate_limit`, `block`) to mitigate DDoS attacks before they compromise the network.

## Architecture

### Dynamic Traffic Simulation Engine

Unlike static scripted environments, CLAIRS features a **physics-based network traffic simulator** that generates realistic traffic patterns:

- **Noise & Jitter** — Every observation includes controlled randomness (±12 %), making each episode unique
- **Action-Responsive Physics** — Agent decisions directly affect traffic: blocking reduces PPS by ~95 %, rate limiting by ~60 %
- **System Health Degradation** — Unmitigated attacks progressively degrade system health, creating urgency for the agent
- **Multi-Phase Attack Patterns** — Attacks progress through probe, ramp, and surge phases with exponential curves
- **Smooth Transitions** — Traffic metrics use exponential moving averages, preventing unrealistic jumps

### Agentic Context Window

The inference agent maintains a **rolling window of the last 3 telemetry snapshots**, allowing the LLM to analyse temporal trends (distinguishing momentary spikes from sustained attacks) before making a strict classification decision. The prompt includes **trend indicators** (SURGING / RISING / STABLE / FALLING) computed from the window.

### Observation Space

| Field | Type | Range | Description |
|---|---|---|---|
| `cpu_usage_percent` | float | 0–100 | CPU load on the IoT gateway |
| `packet_rate_pps` | float | 0–50 000+ | Incoming packets per second |
| `active_connections` | int | 0–6 000+ | Concurrent TCP connections |
| `bandwidth_mbps` | float | 0–60+ | Network bandwidth consumption |
| `memory_usage_percent` | float | 20–95 | Device memory pressure |
| `system_health` | float | 0–100 | Cumulative integrity score |

### Action Space

| Action | Effect | Best For |
|---|---|---|
| `monitor` | No mitigation applied | Normal / benign traffic |
| `rate_limit` | Reduce incoming traffic ~60 % | Moderate / stealth attacks |
| `block` | Drop incoming traffic ~95 % | Severe volumetric floods |

## Tasks

| ID | Difficulty | Scenario | Optimal Strategy |
|---|---|---|---|
| `task_1_easy` | Easy | Normal traffic monitoring | Monitor continuously, avoid false positives |
| `task_2_medium` | Medium | Volumetric DDoS flood (PPS 5k → 50k) | Detect spike, escalate to block |
| `task_3_hard` | Hard | Stealth low-and-slow DDoS | Detect gradual PPS rise, apply rate limiting |
| `task_4_expert` | Expert | Multi-wave APT: probe → retreat → surge | Adapt to deceptive retreat phase |

## Reward Function

Multi-criteria scoring system:

- **Action Correctness** — Primary signal based on current traffic state and attack severity
- **False-Positive Penalty** — Blocking or rate-limiting normal traffic is penalised
- **Early-Detection Bonus** — Catching an attack within the first 3 steps earns extra reward
- **Severity Scaling** — Appropriate escalation for the attack intensity level
- **Health Preservation** — Bonus for maintaining system health above 70 %
- **Task-Specific Nuance** — Stealth attacks (task 3) reward `rate_limit` over `block`

All rewards are clamped to `[0.01, 0.99]` to guarantee mathematical stability within OpenEnv's `(0, 1)` exclusive range.

## Setup & Execution

### 1. Environment Variables

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1/"
export MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
export HF_TOKEN="your_token_here"
```

### 2. Start the Environment Server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### 3. Run the Autonomous Agent

```bash
python inference.py
```

## Engineering Notes

- **Deterministic Fallback** — If the LLM API is unreachable, the agent defaults to `monitor`, which is safe for normal traffic scenarios and prevents inference crashes.
- **Resource Efficient** — Designed to run within `vcpu=2`, `memory=8GB` constraints with no GPU requirement.
- **Typed Models** — All API schemas are defined as shared Pydantic models in `models.py` for strict type safety.
