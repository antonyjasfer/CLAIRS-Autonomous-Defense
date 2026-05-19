import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from server.app import app, NetworkSimulator, ATTACK_PROFILES
from server.models import Observation, StepResponse

client = TestClient(app)

def test_network_simulator_reset():
    sim = NetworkSimulator()

    # Modify internal state to non-defaults
    sim.task_id = "some_other_task"
    sim.step_count = 5
    sim.system_health = 50.0
    sim.false_positives = 3
    sim.attack_detected_step = 2
    sim.cumulative_damage = 25.0

    # Call reset
    obs = sim.reset("task_2_medium")

    # Assert variables are correctly reset
    assert sim.task_id == "task_2_medium"
    assert sim.step_count == 0
    assert sim.system_health == 100.0
    assert sim.false_positives == 0
    assert sim.attack_detected_step is None
    assert sim.cumulative_damage == 0.0

    # Assert observation is returned
    assert isinstance(obs, Observation)

    # Assert that the new traffic metrics are correctly generated
    # First phase of task_2_medium:
    # base_pps = 200, base_cpu = 15.0
    first_phase = ATTACK_PROFILES["task_2_medium"]["phases"][0]
    base_pps = first_phase["base_pps"]
    base_cpu = first_phase["base_cpu"]

    # Check bounds based on randomization
    assert base_pps * 0.88 <= sim.current_pps <= base_pps * 1.12
    assert base_cpu * 0.9 <= sim.current_cpu <= base_cpu * 1.1
    assert 1 <= sim.current_connections
    assert 0.1 <= sim.current_bandwidth <= max(0.1, sim.current_pps * 0.001 * 1.2)
    assert 22.0 <= sim.current_memory <= 33.0

def test_network_simulator_reset_invalid_task_id():
    sim = NetworkSimulator()
    with pytest.raises(KeyError):
        sim.reset("invalid_task_id")

@patch("server.app.simulator.step")
def test_step_endpoint_valid_action(mock_step):
    # Setup mock return value for simulator.step
    mock_obs = Observation(
        cpu_usage_percent=10.0,
        packet_rate_pps=100.0,
        active_connections=10,
        bandwidth_mbps=1.0,
        memory_usage_percent=30.0,
        system_health=100.0
    )
    mock_step.return_value = (mock_obs, 0.5, False, {"test": "info"})

    response = client.post("/step", json={"decision": "rate_limit"})

    assert response.status_code == 200
    data = response.json()

    # Assert StepResponse parsing
    step_resp = StepResponse(**data)
    assert step_resp.reward == 0.5
    assert step_resp.done is False
    assert step_resp.info == {"test": "info"}
    assert step_resp.observation.cpu_usage_percent == 10.0

    # Verify the mock was called correctly
    mock_step.assert_called_once_with("rate_limit")

@patch("server.app.simulator.step")
def test_step_endpoint_invalid_action(mock_step):
    mock_obs = Observation(
        cpu_usage_percent=15.0,
        packet_rate_pps=120.0,
        active_connections=12,
        bandwidth_mbps=1.5,
        memory_usage_percent=35.0,
        system_health=95.0
    )
    mock_step.return_value = (mock_obs, 0.1, True, {"mitigation_applied": "monitor"})

    response = client.post("/step", json={"decision": "INVALID_ACTION"})

    assert response.status_code == 200
    data = response.json()

    step_resp = StepResponse(**data)
    assert step_resp.reward == 0.1
    assert step_resp.done is True
    assert step_resp.observation.cpu_usage_percent == 15.0

    # The endpoint passes the lowercased invalid action to simulator.step.
    # The simulator itself handles defaulting it to "monitor", but the endpoint just passes it lowercased.
    mock_step.assert_called_once_with("invalid_action")

@patch("server.app.simulator.step")
def test_step_endpoint_no_payload(mock_step):
    mock_obs = Observation(
        cpu_usage_percent=12.0,
        packet_rate_pps=110.0,
        active_connections=11,
        bandwidth_mbps=1.2,
        memory_usage_percent=32.0,
        system_health=98.0
    )
    mock_step.return_value = (mock_obs, 0.8, False, {})

    # Call without payload
    response = client.post("/step")

    assert response.status_code == 200
    data = response.json()

    step_resp = StepResponse(**data)
    assert step_resp.reward == 0.8
    assert step_resp.done is False

    # If no payload, endpoint defaults to "monitor"
    mock_step.assert_called_once_with("monitor")
