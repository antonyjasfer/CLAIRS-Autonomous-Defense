import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy_token")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward} done={done} error={error}", flush=True)

def log_end(success, steps, score, rewards):
    print(f"[END] success={success} steps={steps} score={score} rewards={rewards}", flush=True)

def get_action(obs):
    prompt = f"System telemetry: CPU {obs['cpu_usage_percent']}%, PPS {obs['packet_rate_pps']}. Respond with exactly one word: monitor, rate_limit, or block."
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        text = response.choices[0].message.content.strip().lower()
        if "block" in text:
            return "block"
        if "rate" in text:
            return "rate_limit"
        return "monitor"
    except Exception:
        return "monitor"

def run_episode(task_id):
    log_start(task=task_id, env="clairs-network-defense", model=MODEL_NAME)
    
    try:
        res = requests.post("http://127.0.0.1:7860/reset").json()
        obs = res.get("observation", {})
    except Exception:
        obs = {"cpu_usage_percent": 0.0, "packet_rate_pps": 0, "active_connections": 0}

    done = False
    step_count = 0
    rewards = []
    
    while not done and step_count < 10:
        step_count += 1
        action = get_action(obs)
        
        try:
            step_res = requests.post("http://127.0.0.1:7860/step", json={"decision": action}).json()
            obs = step_res.get("observation", obs)
            reward = step_res.get("reward", 0.0)
            done = step_res.get("done", True)
            error = None
        except Exception as e:
            reward = 0.0
            done = True
            error = str(e)
            
        rewards.append(reward)
        log_step(step=step_count, action=action, reward=reward, done=done, error=error)
        
    score = sum(rewards) / len(rewards) if rewards else 0.0
    success = score >= 0.8
    log_end(success=success, steps=step_count, score=score, rewards=rewards)

if __name__ == "__main__":
    tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]
    for t in tasks:
        run_episode(t)
