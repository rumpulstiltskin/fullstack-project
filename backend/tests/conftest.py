import sqlite3

import pytest
from fastapi.testclient import TestClient

from database import apply_schema, get_db, seed
from main import app


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"

    setup = sqlite3.connect(str(db_file))
    setup.row_factory = sqlite3.Row
    setup.execute("PRAGMA foreign_keys = ON")
    apply_schema(setup)
    seed(setup)
    setup.close()

    def get_test_db():
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
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
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}
