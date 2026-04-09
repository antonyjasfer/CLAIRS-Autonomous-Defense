import os
import requests
import sys
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.environ.get("API_KEY", "dummy_key")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-Coder-32B-Instruct")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

def get_action(telemetry_history):
    history_str = " -> ".join(
        [f"(CPU {h['cpu']:.1f}%, PPS {h['pps']:.0f})" for h in telemetry_history]
    )

    prompt = f"""You are CLAIRS, an advanced autonomous IoT network defense AI. 
Analyze the following rolling network telemetry trend over the last few steps:
{history_str}

Evaluate the trend:
- If traffic is low and stable, output 'monitor'.
- If traffic is rising suspiciously or moderately high, output 'rate_limit'.
- If traffic is spiking massively (severe CPU/PPS load), output 'block'.

Respond with EXACTLY ONE WORD from the choices above. No punctuation, no explanation."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise network defense AI. Output only one word."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.1
        )
        action = response.choices[0].message.content.strip().lower()
        
        if "block" in action: 
            return "block"
        if "rate_limit" in action or "limit" in action: 
            return "rate_limit"
        return "monitor"
    except Exception:
        return "monitor"

def run_episode(task_id):
    print(f"[START] task={task_id} env=clairs-network-defense model={MODEL_NAME}")
    
    try:
        res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
        res.raise_for_status()
        obs = res.json()
    except Exception as e:
        print(f"Error resetting environment: {e}")
        return

    total_reward = 0.0
    rewards_list = []
    telemetry_history = []
    
    for step in range(10):
        if isinstance(obs, dict) and "observation" in obs:
            obs_data = obs["observation"]
        else:
            obs_data = obs
            
        current_cpu = obs_data.get("cpu_usage_percent", 0.0) if isinstance(obs_data, dict) else 0.0
        current_pps = obs_data.get("packet_rate_pps", 0.0) if isinstance(obs_data, dict) else 0.0
        
        telemetry_history.append({"cpu": current_cpu, "pps": current_pps})
        
        if len(telemetry_history) > 3:
            telemetry_history.pop(0)

        action = get_action(telemetry_history)
                        
        try:
            res = requests.post(f"{ENV_URL}/step", json={"decision": action})
            res.raise_for_status()
            step_data = res.json()
            
            obs = step_data
            reward = step_data.get("reward", 0.0)
            done = step_data.get("done", False)
            total_reward += reward
            rewards_list.append(f"{reward:.2f}")
            
            done_str = "true" if done else "false"
            print(f"[STEP] step={step+1} action={action} reward={reward:.2f} done={done_str} error=null")
            
            if done: 
                break
        except Exception:
            break
 
    score = total_reward
    
    if score <= 0.0:
        score = 0.01
    elif score >= 1.0:
        score = 0.99

    success = score >= 0.5

    print(f"[END] success={str(success).lower()} steps={len(rewards_list)} score={score:.2f} rewards={','.join(rewards_list)}")

if __name__ == "__main__":
    tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]
    for t in tasks:
        run_episode(t)
