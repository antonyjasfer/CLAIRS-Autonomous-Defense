from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import random
import math

from models import Observation, Action, StepResponse

app = FastAPI(
    title="CLAIRS Autonomous Defense Environment",
    description="OpenEnv-compliant RL environment for IoT DDoS mitigation",
    version="2.0.0",
)


class ResetRequest(BaseModel):
    task_id: str = "task_1_easy"


class ActionPayload(BaseModel):
    decision: str = "monitor"


ATTACK_PROFILES = {
    "task_1_easy": {
        "name": "Normal Traffic Monitoring",
        "phases": [
            {
                "start": 0,
                "end": 10,
                "type": "normal",
                "base_pps": 120,
                "base_cpu": 10.0,
            },
        ],
    },
    "task_2_medium": {
        "name": "Volumetric DDoS Flood",
        "phases": [
            {
                "start": 0,
                "end": 2,
                "type": "normal",
                "base_pps": 200,
                "base_cpu": 15.0,
            },
            {
                "start": 2,
                "end": 10,
                "type": "attack_ramp",
                "pps_start": 5000,
                "pps_end": 50000,
                "cpu_start": 55.0,
                "cpu_end": 99.0,
            },
        ],
    },
    "task_3_hard": {
        "name": "Stealth Low-and-Slow DDoS",
        "phases": [
            {
                "start": 0,
                "end": 2,
                "type": "normal",
                "base_pps": 150,
                "base_cpu": 12.0,
            },
            {
                "start": 2,
                "end": 10,
                "type": "attack_ramp",
                "pps_start": 2000,
                "pps_end": 25000,
                "cpu_start": 30.0,
                "cpu_end": 75.0,
            },
        ],
    },
    "task_4_expert": {
        "name": "Multi-Wave APT Campaign",
        "phases": [
            {
                "start": 0,
                "end": 2,
                "type": "normal",
                "base_pps": 130,
                "base_cpu": 11.0,
            },
            {
                "start": 2,
                "end": 5,
                "type": "attack_ramp",
                "pps_start": 4000,
                "pps_end": 12000,
                "cpu_start": 40.0,
                "cpu_end": 60.0,
            },
            {
                "start": 5,
                "end": 7,
                "type": "normal",
                "base_pps": 180,
                "base_cpu": 13.0,
            },
            {
                "start": 7,
                "end": 10,
                "type": "attack_ramp",
                "pps_start": 15000,
                "pps_end": 45000,
                "cpu_start": 70.0,
                "cpu_end": 99.0,
            },
        ],
    },
}


class NetworkSimulator:

    def __init__(self):
        self.task_id = "task_1_easy"
        self.step_count = 0
        self.max_steps = 10
        self.system_health = 100.0
        self.current_pps = 100.0
        self.current_cpu = 10.0
        self.current_connections = 10
        self.current_bandwidth = 1.0
        self.current_memory = 30.0
        self.false_positives = 0
        self.attack_detected_step = None
        self.cumulative_damage = 0.0

    def reset(self, task_id: str) -> Observation:
        self.task_id = task_id
        self.step_count = 0
        self.system_health = 100.0
        self.false_positives = 0
        self.attack_detected_step = None
        self.cumulative_damage = 0.0

        first_phase = ATTACK_PROFILES[task_id]["phases"][0]

        noise = random.uniform(0.88, 1.12)
        self.current_pps = first_phase["base_pps"] * noise
        self.current_cpu = min(100.0, first_phase["base_cpu"] * random.uniform(0.9, 1.1))
        self.current_connections = max(1, int(self.current_pps / 8 + random.randint(-5, 5)))
        self.current_bandwidth = max(0.1, self.current_pps * 0.001 * random.uniform(0.8, 1.2))
        self.current_memory = 25.0 + random.uniform(-3, 8)

        return self._observation()

    def step(self, action: str):
        action = action.lower().strip()
        if action not in ("monitor", "rate_limit", "block"):
            action = "monitor"

        reward = self._compute_reward(action)
        self._advance_traffic(action)

        self.step_count += 1
        done = self.step_count >= self.max_steps

        info = {
            "mitigation_applied": action,
            "is_attack_phase": self._is_attack(),
            "attack_severity": round(self._severity(), 2),
            "system_health": round(self.system_health, 1),
            "false_positives": self.false_positives,
            "cumulative_damage": round(self.cumulative_damage, 1),
        }

        return self._observation(), reward, done, info

    def get_state(self) -> Observation:
        return self._observation()

    def _current_phase(self) -> dict:
        for phase in ATTACK_PROFILES[self.task_id]["phases"]:
            if phase["start"] <= self.step_count < phase["end"]:
                return phase
        return ATTACK_PROFILES[self.task_id]["phases"][-1]

    def _is_attack(self) -> bool:
        return self._current_phase()["type"] == "attack_ramp"

    def _severity(self) -> float:
        phase = self._current_phase()
        if phase["type"] != "attack_ramp":
            return 0.0
        span = max(1, phase["end"] - phase["start"] - 1)
        return min(1.0, (self.step_count - phase["start"]) / span)

    def _advance_traffic(self, action: str):
        phase = self._current_phase()
        noise = random.uniform(0.88, 1.12)

        mitigation = 1.0
        if action == "block":
            mitigation = 0.05 + random.uniform(0, 0.03)
        elif action == "rate_limit":
            mitigation = 0.35 + random.uniform(0, 0.08)

        if phase["type"] == "normal":
            target_pps = phase["base_pps"] * noise
            target_cpu = phase["base_cpu"] * random.uniform(0.9, 1.1)
        else:
            span = max(1, phase["end"] - phase["start"] - 1)
            progress = (self.step_count - phase["start"]) / span
            ramp = min(1.0, progress ** 1.3)

            raw_pps = phase["pps_start"] + (phase["pps_end"] - phase["pps_start"]) * ramp
            raw_cpu = phase["cpu_start"] + (phase["cpu_end"] - phase["cpu_start"]) * ramp

            target_pps = raw_pps * noise * mitigation
            target_cpu = min(100.0, raw_cpu * noise * (0.3 + 0.7 * mitigation))

        alpha = 0.7
        self.current_pps = (1 - alpha) * self.current_pps + alpha * target_pps
        self.current_cpu = (1 - alpha) * self.current_cpu + alpha * target_cpu
        self.current_connections = max(1, int(self.current_pps / 8 + random.randint(-3, 3)))
        self.current_bandwidth = max(0.1, self.current_pps * 0.001 * random.uniform(0.85, 1.15))

        mem_delta = random.uniform(-2, 3)
        if self._is_attack() and action == "monitor":
            mem_delta += self._severity() * 4
        self.current_memory = max(20.0, min(95.0, self.current_memory + mem_delta))

        if self._is_attack() and action == "monitor":
            dmg = self._severity() * random.uniform(3.0, 7.0)
            self.system_health = max(0.0, self.system_health - dmg)
            self.cumulative_damage += dmg
        elif self._is_attack() and action == "rate_limit":
            dmg = self._severity() * random.uniform(0.5, 2.0)
            self.system_health = max(0.0, self.system_health - dmg)
            self.cumulative_damage += dmg
        else:
            self.system_health = min(100.0, self.system_health + random.uniform(0.3, 1.0))

    def _compute_reward(self, action: str) -> float:
        is_attack = self._is_attack()
        severity = self._severity()
        reward = 0.50

        if not is_attack:
            if action == "monitor":
                reward = 0.90 + random.uniform(0, 0.08)
            elif action == "rate_limit":
                reward = 0.25 + random.uniform(0, 0.08)
                self.false_positives += 1
            elif action == "block":
                reward = 0.08 + random.uniform(0, 0.06)
                self.false_positives += 1
        else:
            if severity > 0.6:
                if action == "block":
                    reward = 0.88 + random.uniform(0, 0.09)
                elif action == "rate_limit":
                    reward = 0.48 + random.uniform(0, 0.10)
                else:
                    reward = 0.03 + random.uniform(0, 0.05)
            elif severity > 0.2:
                if action == "rate_limit":
                    reward = 0.85 + random.uniform(0, 0.09)
                elif action == "block":
                    reward = 0.58 + random.uniform(0, 0.10)
                else:
                    reward = 0.05 + random.uniform(0, 0.07)
            else:
                if action in ("rate_limit", "block"):
                    reward = 0.78 + random.uniform(0, 0.10)
                else:
                    reward = 0.10 + random.uniform(0, 0.08)

            if self.attack_detected_step is None and action in ("rate_limit", "block"):
                self.attack_detected_step = self.step_count
                if self.step_count <= 3:
                    reward = min(0.99, reward + 0.04)

        if self.task_id == "task_3_hard" and is_attack:
            if action == "rate_limit":
                reward = min(0.99, reward + 0.04)
            elif action == "block" and severity < 0.5:
                reward = max(0.01, reward - 0.08)

        if self.system_health > 70:
            reward = min(0.99, reward + 0.02)

        return round(max(0.01, min(0.99, reward)), 4)

    def _observation(self) -> Observation:
        return Observation(
            cpu_usage_percent=round(self.current_cpu, 2),
            packet_rate_pps=round(self.current_pps, 2),
            active_connections=max(0, self.current_connections),
            bandwidth_mbps=round(self.current_bandwidth, 2),
            memory_usage_percent=round(self.current_memory, 2),
            system_health=round(self.system_health, 2),
        )


simulator = NetworkSimulator()


@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_id = req.task_id if req else "task_1_easy"
    if task_id not in ATTACK_PROFILES:
        task_id = "task_1_easy"

    obs = simulator.reset(task_id)
    return obs.model_dump()


@app.post("/step", response_model=StepResponse)
def step(payload: Optional[ActionPayload] = None):
    action = payload.decision.lower() if payload else "monitor"
    obs, reward, done, info = simulator.step(action)

    return StepResponse(observation=obs, reward=reward, done=done, info=info)


@app.get("/state", response_model=Observation)
def state():
    return simulator.get_state()


@app.get("/health")
def health():
    return {"status": "ok"}


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
