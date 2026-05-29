import pytest
from fastapi.testclient import TestClient

from database import apply_schema, get_db, open_db, seed
from main import app
from rate_limit import clear_all as clear_rate_limits


@pytest.fixture(autouse=True)
def reset_rate_limits():
    clear_rate_limits()
    yield
    clear_rate_limits()


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"

    setup = open_db(db_file)
    apply_schema(setup)
    seed(setup)
    setup.close()

    def get_test_db():
        conn = open_db(db_file)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    res = client.post("/api/auth/login", json={"username": "user", "password": "password"})
    assert res.status_code == 200
    return {}
