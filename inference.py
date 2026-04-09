import os
import requests
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.environ.get("API_KEY", "dummy")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-Coder-32B-Instruct")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

def get_action(telemetry_history):
    history_str = " -> ".join(
        [f"(CPU {h['cpu']:.1f}%, PPS {h['pps']:.0f})" for h in telemetry_history]
    )

    prompt = f"""Analyze the following network telemetry trend: {history_str}
Choices: monitor, rate_limit, block. Respond with exactly one word."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a network defense AI. Output only one word."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5,
            temperature=0.1
        )
        action = response.choices[0].message.content.strip().lower()
        if "block" in action: return "block"
        if "rate_limit" in action or "limit" in action: return "rate_limit"
        return "monitor"
    except:
        return "monitor"

def run_episode(task_id):
    print(f"[START] task={task_id}")
    try:
        res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
        obs = res.json()
    except:
        return

    total_reward = 0.0
    rewards_list = []
    telemetry_history = []
    
    for step in range(10):
        if isinstance(obs, dict) and "observation" in obs:
            obs_data = obs["observation"]
        else:
            obs_data = obs
            
        cpu = obs_data.get("cpu_usage_percent", 0.0)
        pps = obs_data.get("packet_rate_pps", 0.0)
        telemetry_history.append({"cpu": cpu, "pps": pps})
        
        if len(telemetry_history) > 3:
            telemetry_history.pop(0)

        action = get_action(telemetry_history)
                        
        try:
            res = requests.post(f"{ENV_URL}/step", json={"decision": action})
            step_data = res.json()
            obs = step_data
            reward = step_data.get("reward", 0.0)
            total_reward += reward
            rewards_list.append(f"{reward:.2f}")
            if step_data.get("done", False): break
        except:
            break
 
    score = max(0.01, min(0.99, total_reward))
    success = score >= 0.5
    print(f"[END] success={str(success).lower()} steps={len(rewards_list)} score={score:.2f} rewards={','.join(rewards_list)}")

if __name__ == "__main__":
    for t in ["task_1_easy", "task_2_medium", "task_3_hard"]:
        run_episode(t)
