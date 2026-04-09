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
    done_str = "true" if done else "false"
    err_str = "null" if error is None else f'"{error}"'
    print(f"[STEP] step={step} action={action} reward={float(reward):.2f} done={done_str} error={err_str}", flush=True)

def log_end(success, steps, score, rewards):
    succ_str = "true" if success else "false"
    rews_str = ",".join([f"{float(r):.2f}" for r in rewards])
    print(f"[END] success={succ_str} steps={steps} score={score:.2f} rewards={rews_str}", flush=True)

def get_action(history):
    history_str = " -> ".join([f"(CPU {h['cpu']:.1f}%, PPS {h['pps']:.0f})" for h in history])
    prompt = f"System telemetry trend: {history_str}. Respond with exactly one word: monitor, rate_limit, or block."
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict network defense AI. Output only one word."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.1
        )
        text = response.choices[0].message.content.strip().lower()
        if "block" in text:
            return "block"
        if "limit" in text or "rate" in text:
            return "rate_limit"
        return "monitor"
    except Exception:
        return "monitor"

def run_episode(task_id):
    log_start(task=task_id, env="clairs-network-defense", model=MODEL_NAME)
    
    try:
        res = requests.post("http://127.0.0.1:7860/reset", json={"task_id": task_id}).json()
        obs = res if "cpu_usage_percent" in res else res.get("observation", {})
    except Exception:
        obs = {"cpu_usage_percent": 0.0, "packet_rate_pps": 0.0, "active_connections": 0}

    done = False
    step_count = 0
    rewards = []
    history = []
    
    while not done and step_count < 10:
        step_count += 1
        
        cpu = obs.get("cpu_usage_percent", 0.0)
        pps = obs.get("packet_rate_pps", 0.0)
        history.append({"cpu": cpu, "pps": pps})
        
        if len(history) > 3:
            history.pop(0)
            
        action = get_action(history)
        
        try:
            step_res = requests.post("http://127.0.0.1:7860/step", json={"decision": action}).json()
            obs = step_res.get("observation", obs)
            reward = step_res.get("reward", 0.01)
            done = step_res.get("done", True)
            error = None
        except Exception as e:
            reward = 0.01
            done = True
            error = str(e)
            
        rewards.append(reward)
        log_step(step=step_count, action=action, reward=reward, done=done, error=error)
        
    raw_score = sum(rewards) / len(rewards) if rewards else 0.01
    score = max(0.01, min(0.99, raw_score))
    success = score >= 0.8
    log_end(success=success, steps=step_count, score=score, rewards=rewards)

if __name__ == "__main__":
    tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]
    for t in tasks:
        run_episode(t)
