def test_login_success(client):
    res = client.post("/api/auth/login", json={"username": "user", "password": "password"})
    assert res.status_code == 200
    assert res.json() == {"ok": True}
    assert "session" in res.cookies


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"username": "user", "password": "wrong"})
    assert res.status_code == 401


def test_login_wrong_username(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "password"})
    assert res.status_code == 401


def test_logout_success(client, auth_headers):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200


def test_logout_invalidates_session(client, auth_headers):
    client.post("/api/auth/logout")
    res = client.post("/api/auth/logout")
    assert res.status_code == 401


def test_request_without_session_is_rejected(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 401


def test_request_with_invalid_session_is_rejected(client):
    res = client.post("/api/auth/logout", cookies={"session": "notavalidtoken"})
    assert res.status_code == 401
