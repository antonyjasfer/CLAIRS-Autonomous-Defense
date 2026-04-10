import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy_token")

ENV_URL = "http://127.0.0.1:7860"

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    done_str = "true" if done else "false"
    err_str = "null" if error is None else f'"{error}"'
    print(
        f"[STEP] step={step} action={action} reward={float(reward):.2f} "
        f"done={done_str} error={err_str}",
        flush=True,
    )


def log_end(success, steps, score, rewards):
    succ_str = "true" if success else "false"
    rews_str = ",".join([f"{float(r):.2f}" for r in rewards])
    print(
        f"[END] success={succ_str} steps={steps} score={score:.2f} rewards={rews_str}",
        flush=True,
    )


def _classify_trend(history, key):
    if len(history) < 2:
        return "UNKNOWN"
    delta = history[-1][key] - history[0][key]
    if key == "pps":
        if delta > 1000:
            return "SURGING"
        if delta > 200:
            return "RISING"
        if delta < -200:
            return "FALLING"
    else:
        if delta > 10:
            return "RISING"
        if delta < -5:
            return "FALLING"
    return "STABLE"


def get_action(history):
    entries = []
    for h in history:
        entries.append(
            f"(CPU {h['cpu']:.1f}%, PPS {h['pps']:.0f}, "
            f"BW {h['bw']:.1f}Mbps, Health {h['health']:.0f}%)"
        )
    telemetry = " -> ".join(entries)

    pps_trend = _classify_trend(history, "pps")
    cpu_trend = _classify_trend(history, "cpu")

    prompt = (
        f"Network telemetry (last {len(history)} snapshots):\n"
        f"  {telemetry}\n"
        f"PPS trend: {pps_trend}  |  CPU trend: {cpu_trend}\n\n"
        f"Respond with exactly one word: monitor, rate_limit, or block."
    )

    system_msg = (
        "You are a strict IoT network defense AI protecting critical infrastructure. "
        "Analyse the telemetry trend and choose the optimal mitigation action. "
        "Output ONLY one word — no explanation."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            max_tokens=10,
            temperature=0.1,
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
        res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}).json()
        obs = res if "cpu_usage_percent" in res else res.get("observation", {})
    except Exception:
        obs = {
            "cpu_usage_percent": 0.0,
            "packet_rate_pps": 0.0,
            "active_connections": 0,
            "bandwidth_mbps": 0.0,
            "memory_usage_percent": 30.0,
            "system_health": 100.0,
        }

    done = False
    step_count = 0
    rewards = []
    history = []

    while not done and step_count < 10:
        step_count += 1

        cpu = obs.get("cpu_usage_percent", 0.0)
        pps = obs.get("packet_rate_pps", 0.0)
        bw = obs.get("bandwidth_mbps", 0.0)
        health = obs.get("system_health", 100.0)
        history.append({"cpu": cpu, "pps": pps, "bw": bw, "health": health})

        if len(history) > 3:
            history.pop(0)

        action = get_action(history)

        try:
            step_res = requests.post(
                f"{ENV_URL}/step", json={"decision": action}
            ).json()
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
    success = score >= 0.5
    log_end(success=success, steps=step_count, score=score, rewards=rewards)


if __name__ == "__main__":
    tasks = ["task_1_easy", "task_2_medium", "task_3_hard", "task_4_expert"]
    for t in tasks:
        run_episode(t)
