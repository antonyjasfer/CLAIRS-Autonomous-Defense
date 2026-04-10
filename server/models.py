from pydantic import BaseModel, Field
from typing import Dict, Any


class Observation(BaseModel):
    cpu_usage_percent: float = Field(
        ...,
        description="Current CPU load of the IoT gateway (0.0 to 100.0).",
    )
    packet_rate_pps: float = Field(
        ...,
        description="Incoming packets per second observed at the network interface.",
    )
    active_connections: int = Field(
        ...,
        description="Number of concurrent TCP connections to the device.",
    )
    bandwidth_mbps: float = Field(
        ...,
        description="Current bandwidth consumption in megabits per second.",
    )
    memory_usage_percent: float = Field(
        ...,
        description="Device memory utilization (0.0 to 100.0).",
    )
    system_health: float = Field(
        ...,
        description="Cumulative system integrity score (0.0 to 100.0). "
        "Degrades under sustained unmitigated attacks.",
    )


class Action(BaseModel):
    decision: str = Field(
        ...,
        description="The mitigation action to apply. "
        "Must be one of: 'monitor', 'rate_limit', or 'block'.",
    )


class StepResponse(BaseModel):
    observation: Observation
    reward: float = Field(
        ...,
        description="Reward score for the agent's action (strictly 0.0 to 1.0).",
    )
    done: bool = Field(
        ...,
        description="Whether the episode has terminated.",
    )
    info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostic metadata: attack phase, severity, health, etc.",
    )
