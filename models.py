from pydantic import BaseModel, Field

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

class Action(BaseModel):
    decision: str = Field(kjb
        ..., 
        description="The mitigation action to take. Must be one of: 'monitor', 'rate_limit', or 'block'."
    )

class Reward(BaseModel):
    score: float = Field(
        ..., 
        description="The reward score for the action taken, strictly between 0.0 and 1.0."
    )
    reasoning: str = Field(
        ..., 
        description="Explanation for why this reward was given."
    )
