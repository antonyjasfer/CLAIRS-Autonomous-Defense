from pydantic import BaseModel, Field

# 1. What the AI SEES (The State/Telemetry)
class Observation(BaseModel):
    cpu_usage_percent: float = Field(
        ..., 
        description="Current CPU load of the IoT device/server (0.0 to 100.0)."
    )
    packet_rate_pps: int = Field(
        ..., 
        description="Current incoming packets per second."
    )
    active_connections: int = Field(
        ..., 
        description="Number of active connections to the device."
    )

# 2. What the AI DOES (The Decision)
class Action(BaseModel):
    decision: str = Field(
        ..., 
        description="The mitigation action to take. Must be one of: 'monitor', 'rate_limit', or 'block'."
    )

# 3. How the AI is SCORED (The Grade)
class Reward(BaseModel):
    score: float = Field(
        ..., 
        description="The reward score for the action taken, strictly between 0.0 and 1.0."
    )
    reasoning: str = Field(
        ..., 
        description="Explanation for why this reward was given."
    )
