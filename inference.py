import os
import requests
import sys

ENV_URL = "http://localhost:7860"

def run_episode(task_id):
    print(f"[START] Task {task_id}")
    
    try:
        res = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
        res.raise_for_status()
        obs = res.json()
    except Exception as e:
        print(f"Failed to reset: {e}")
        return

    total_reward = 0.0
    
    for step in range(10):
        if step < 5:
            if task_id == "task_1_easy": 
                action = "monitor"
            elif task_id == "task_2_medium": 
                action = "block"
            else: 
                action = "rate_limit"
        else:
            action = "wrong_action_on_purpose"
            
        try:
            res = requests.post(f"{ENV_URL}/step", json={"action": action})
            res.raise_for_status()
            step_data = res.json()
            
            reward = step_data.get("reward", 0.0)
            done = step_data.get("done", False)
            total_reward += reward
            
            print(f"[STEP] Action: {action} | Reward: {reward}")
            if done: 
                break
        except Exception as e:
            break
            
    print(f"[END] Total Reward: {total_reward}")

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "task_1_easy"
    run_episode(task)
