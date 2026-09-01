import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from server.app import app
from server.models import Observation, StepResponse

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("server.app.random.uniform", return_value=1.0)
@patch("server.app.random.randint", return_value=0)
def test_reset_endpoint(mock_randint, mock_uniform):
    # Test default reset
    response = client.post("/reset")
    assert response.status_code == 200
    data = response.json()

    # Unpack to validate Pydantic schema
    obs = Observation(**data)
    assert obs.system_health == 100.0

    # Test reset with explicit task_id
    response = client.post("/reset", json={"task_id": "task_2_medium"})
    assert response.status_code == 200
    data = response.json()
    obs = Observation(**data)
    assert obs.system_health == 100.0

    # Test reset with invalid task_id (should fallback to default task_1_easy)
    response = client.post("/reset", json={"task_id": "invalid_task"})
    assert response.status_code == 200
    data = response.json()
    obs = Observation(**data)
    assert obs.system_health == 100.0


@patch("server.app.random.uniform", return_value=1.0)
@patch("server.app.random.randint", return_value=0)
def test_state_endpoint(mock_randint, mock_uniform):
    client.post("/reset")
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    obs = Observation(**data)
    assert obs.system_health == 100.0


@patch("server.app.random.uniform", return_value=1.0)
@patch("server.app.random.randint", return_value=0)
def test_step_endpoint(mock_randint, mock_uniform):
    client.post("/reset")

    # Test step with monitor
    response = client.post("/step", json={"decision": "monitor"})
    assert response.status_code == 200
    data = response.json()
    step_resp = StepResponse(**data)
    assert "mitigation_applied" in step_resp.info
    assert step_resp.info["mitigation_applied"] == "monitor"

    # Test step with rate_limit
    response = client.post("/step", json={"decision": "rate_limit"})
    assert response.status_code == 200
    data = response.json()
    step_resp = StepResponse(**data)
    assert step_resp.info["mitigation_applied"] == "rate_limit"

    # Test step with block
    response = client.post("/step", json={"decision": "block"})
    assert response.status_code == 200
    data = response.json()
    step_resp = StepResponse(**data)
    assert step_resp.info["mitigation_applied"] == "block"

    # Test step with invalid action (should fallback to monitor)
    response = client.post("/step", json={"decision": "invalid"})
    assert response.status_code == 200
    data = response.json()
    step_resp = StepResponse(**data)
    assert step_resp.info["mitigation_applied"] == "monitor"

    # Test missing payload
    response = client.post("/step")
    assert response.status_code == 200
    data = response.json()
    step_resp = StepResponse(**data)
    assert step_resp.info["mitigation_applied"] == "monitor"


@patch("server.app.random.uniform", return_value=1.0)
@patch("server.app.random.randint", return_value=0)
def test_step_until_done(mock_randint, mock_uniform):
    client.post("/reset")
    for _ in range(9):
        response = client.post("/step", json={"decision": "monitor"})
        data = response.json()
        step_resp = StepResponse(**data)
        assert not step_resp.done

    # The 10th step should mark done=True (since max_steps=10)
    response = client.post("/step", json={"decision": "monitor"})
    data = response.json()
    step_resp = StepResponse(**data)
    assert step_resp.done
