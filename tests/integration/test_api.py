import pytest
from fastapi.testclient import TestClient
from src.app import app

# This fixture keeps the application and event loop open 
# for the entire test session (scope="module").
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Verify the API is online"""
    response = client.get("/health")
    assert response.status_code == 200

def test_register_client(client):
    """Verify we can register a new client"""
    response = client.post("/api/v1/clients", json={
        "clientId": "automated-test-app",
        "apiKey": "test-secret-key",
        "maxRequests": 3,
        "windowSeconds": 60
    })
    # We expect 201 (Created) or 409 (Conflict if it already ran once)
    assert response.status_code in [201, 409]

def test_rate_limit_enforcement(client):
    """Verify the Token Bucket actually blocks traffic"""
    # 1. Hit the API 3 times (Our limit is 3)
    for _ in range(3):
        res = client.post("/api/v1/ratelimit/check", json={
            "clientId": "automated-test-app",
            "path": "/api/test"
        })
        assert res.status_code == 200
        assert res.json()["allowed"] == True

    # 2. Hit it a 4th time and verify it gets blocked!
    blocked_res = client.post("/api/v1/ratelimit/check", json={
        "clientId": "automated-test-app",
        "path": "/api/test"
    })
    assert blocked_res.status_code == 429
    assert blocked_res.json()["allowed"] == False