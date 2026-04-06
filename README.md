# 🛡️ CLAIRS: Lightweight Autonomous Defense for IoT Networks

**An interactive, hybrid-AI defense environment designed to detect and mitigate DDoS attacks in real time for resource-constrained IoT systems.**

## 📖 Problem Statement
Low-power IoT devices—such as factory sensors, smart cameras, and embedded systems—are highly vulnerable to hijacking due to their limited computational capacity. These compromised devices are often used to form large botnets that launch Distributed Denial-of-Service (DDoS) attacks.

Traditional security solutions are too resource-intensive to run on such devices. At the same time, many academic AI-based cybersecurity projects rely on static datasets and offline evaluation, which do not reflect real-world conditions.

Our goal was to design a system that is both lightweight and adaptive, while supporting real-time decision-making.

## 🧠 Our Approach: Hybrid AI Architecture
CLAIRS is built as a closed-loop, interactive environment rather than a static detection model.

A key design challenge was latency. While Large Language Models (LLMs) provide strong reasoning capabilities, they are not suitable for real-time mitigation due to response delays.

To address this, we implemented a hybrid architecture:

### ⚡ Fast Reflex Layer (Scikit-Learn)
* A lightweight, custom-trained model processes live telemetry (CPU usage, packet rate)
* Executes decisions—Monitor, Rate Limit, Block—within milliseconds
* Ensures immediate response to threats

### 🧠 Deep Analysis Layer (Hugging Face LLM)
* Triggered after mitigation
* Generates human-readable threat analysis based on telemetry
* Provides interpretability without affecting real-time performance
* This analysis is generated asynchronously and displayed in the live audit log.

This separation enables both low-latency response and high-level reasoning, similar to real-world security systems.

## ⚙️ Environment Design
The system is powered by a custom FastAPI backend that simulates a dynamic network environment. At each timestep, the system observes network state, selects an action, updates the environment, and assigns a reward—forming a continuous decision loop.

### 🌪️ Chaos Engine
Continuously generates synthetic traffic and supports multiple difficulty levels:
* **Easy:** Normal traffic patterns
* **Medium:** Volumetric DDoS spikes
* **Hard:** Stealth attacks (low CPU, high packet rate)

### 🎯 Reward System
The agent is evaluated using a normalized reward framework:
* **Rewards:** `+0.40` → correct mitigation or correct pass-through
* **Penalties:** `-0.30` → false positives or incorrect actions

The system is optimized to balance security and service continuity.

## 🛠️ Tech Stack
* **AI / ML:** Python, Scikit-Learn (Joblib), Hugging Face LLM (via OpenAI-compatible API)
* **Backend:** FastAPI, Uvicorn (async server, port 7860 for deployment)
* **Frontend:** HTML5, JavaScript, Tailwind CSS, Chart.js (real-time visualization)
* **Deployment:** Docker, Hugging Face Spaces

## 🚀 Running Locally
To run the environment locally:

```bash
git clone <repo-url>
cd <repo-folder>
pip install fastapi uvicorn pandas scikit-learn joblib openai
python3 live_defense.py
