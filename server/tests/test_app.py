from fastapi.testclient import TestClient
from server.app import app, ATTACK_PROFILES
from server.models import Observation

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_reset_no_payload():
    response = client.post("/reset")
    assert response.status_code == 200
    data = response.json()
    # Validate structure using the Observation model
    Observation(**data)

def test_reset_valid_task():
    response = client.post("/reset", json={"task_id": "task_2_medium"})
    assert response.status_code == 200
    data = response.json()
    Observation(**data)

def test_reset_invalid_task():
    response = client.post("/reset", json={"task_id": "invalid_task"})
    assert response.status_code == 200
    data = response.json()
    Observation(**data)
