import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _login() -> str:
    res = client.post("/api/auth/login", json={"username": "user", "password": "password"})
    assert res.status_code == 200
    return res.json()["token"]


def test_login_success():
    res = client.post("/api/auth/login", json={"username": "user", "password": "password"})
    assert res.status_code == 200
    assert "token" in res.json()
    assert len(res.json()["token"]) > 0


def test_login_wrong_password():
    res = client.post("/api/auth/login", json={"username": "user", "password": "wrong"})
    assert res.status_code == 401


def test_login_wrong_username():
    res = client.post("/api/auth/login", json={"username": "admin", "password": "password"})
    assert res.status_code == 401


def test_logout_success():
    token = _login()
    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200


def test_logout_invalidates_token():
    token = _login()
    client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


def test_request_without_token_is_rejected():
    res = client.post("/api/auth/logout")
    assert res.status_code == 422  # missing required header


def test_request_with_invalid_token_is_rejected():
    res = client.post("/api/auth/logout", headers={"Authorization": "Bearer notavalidtoken"})
    assert res.status_code == 401
