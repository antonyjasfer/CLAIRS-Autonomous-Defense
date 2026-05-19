import pytest
from fastapi.testclient import TestClient
from server.app import app, NetworkSimulator, ATTACK_PROFILES
from server.models import Observation

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

def test_reset_endpoint_default():
    response = client.post("/reset")
    assert response.status_code == 200
    data = response.json()
    obs = Observation(**data)
    assert obs.system_health == 100.0

def test_reset_endpoint_valid_task():
    response = client.post("/reset", json={"task_id": "task_2_medium"})
    assert response.status_code == 200
    data = response.json()
    obs = Observation(**data)
    assert obs.system_health == 100.0

def test_reset_endpoint_invalid_task():
    response = client.post("/reset", json={"task_id": "invalid_task"})
    assert response.status_code == 200
    data = response.json()
    obs = Observation(**data)
    assert obs.system_health == 100.0
