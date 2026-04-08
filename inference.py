import os
import requests
import sys
from openai import OpenAI

API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-Coder-32B-Instruct")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

def get_action(obs):
    if isinstance(obs, dict) and "observation" in obs:
        obs_data = obs["observation"]
    else:
        obs_data = obs
        
    if isinstance(obs_data, dict):
        cpu = obs_data.get("cpu_usage_percent", 0.0)
        pps = obs_data.get("packet_rate_pps", 0.0)
    else:
        cpu = 0.0
        pps = 0.0

    prompt = f"System telemetry: CPU {cpu}%, PPS {pps}. Respond with exactly one word: monitor, rate_limit, or block."

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a network defense AI. Output only one word."},
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
    except Exception:
        return

    total_reward = 0.0
    rewards_list = []
    
    for step in range(10):
        action = get_action(obs)
            
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
            
    avg_score = total_reward / max(len(rewards_list), 1)

    if avg_score <= 0.0:
        avg_score = 0.01
    elif avg_score >= 1.0:
        avg_score = 0.99

    success = avg_score >= 0.6

    print(f"[END] success={str(success).lower()} steps={len(rewards_list)} rewards={','.join(rewards_list)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_episode(sys.argv[1])
    else:
        tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]
        for t in tasks:
            run_episode(t)
