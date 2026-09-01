import pytest
from fastapi.testclient import TestClient
from server.app import app
from server.models import Observation, StepResponse

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_state():
    response = client.get("/state")
    assert response.status_code == 200
    # ensure it's a valid observation
    obs = Observation(**response.json())
    assert obs.system_health is not None


def test_reset_default():
    response = client.post("/reset")
    assert response.status_code == 200
    obs = Observation(**response.json())
    assert obs.system_health == 100.0

def test_reset_with_payload():
    response = client.post("/reset", json={"task_id": "task_2_medium"})
    assert response.status_code == 200
    obs = Observation(**response.json())
    assert obs.system_health == 100.0

def test_reset_with_invalid_payload():
    response = client.post("/reset", json={"task_id": "invalid_task_id"})
    assert response.status_code == 200
    obs = Observation(**response.json())
    assert obs.system_health == 100.0


def test_step_default():
    response = client.post("/step")
    assert response.status_code == 200
    res = StepResponse(**response.json())
    assert res.info["mitigation_applied"] == "monitor"
    assert res.reward > 0

def test_step_with_payload():
    response = client.post("/step", json={"decision": "block"})
    assert response.status_code == 200
    res = StepResponse(**response.json())
    assert res.info["mitigation_applied"] == "block"
    assert res.reward > 0
