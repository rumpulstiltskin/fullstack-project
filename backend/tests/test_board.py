def test_get_board_returns_seeded_columns(client, auth_headers):
    res = client.get("/api/board", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["columns"]) == 5
    assert data["columns"][0]["title"] == "Backlog"
    assert isinstance(data["cards"], dict)


def test_get_board_requires_auth(client):
    res = client.get("/api/board")
    assert res.status_code == 422  # missing Authorization header

    res = client.get("/api/board", headers={"Authorization": "Bearer bad"})
    assert res.status_code == 401


def test_put_board_replaces_state(client, auth_headers):
    initial = client.get("/api/board", headers=auth_headers).json()

    # Rename first column and add a card to it
    board = dict(initial)
    board["columns"] = list(board["columns"])
    board["columns"][0] = dict(board["columns"][0])
    board["columns"][0]["title"] = "Priority Queue"
    board["columns"][0]["cardIds"] = ["card-new-1"]
    board["cards"] = {"card-new-1": {"id": "card-new-1", "title": "First task", "details": "Details here"}}

    res = client.put("/api/board", json=board, headers=auth_headers)
    assert res.status_code == 200

    updated = client.get("/api/board", headers=auth_headers).json()
    assert updated["columns"][0]["title"] == "Priority Queue"
    assert "card-new-1" in updated["cards"]
    assert updated["cards"]["card-new-1"]["title"] == "First task"


def test_put_board_requires_auth(client):
    res = client.put("/api/board", json={"columns": [], "cards": {}})
    assert res.status_code == 422
