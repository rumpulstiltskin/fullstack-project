from unittest.mock import patch

from models import AIResponse, BoardData, Card, Column


def _mock_board() -> BoardData:
    return BoardData(
        columns=[Column(id="col-backlog", title="Backlog", cardIds=[])],
        cards={},
    )


def test_chat_returns_message_without_board_update(client, auth_headers):
    with patch("routers.chat.call_ai_structured") as mock_ai:
        mock_ai.return_value = AIResponse(message="Hello!", board_update=None)
        res = client.post(
            "/api/chat",
            json={"history": [], "user_message": "Hello"},
            headers=auth_headers,
        )
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "Hello!"
    assert data["board_update"] is None


def test_chat_returns_board_update(client, auth_headers):
    new_board = _mock_board()
    new_board.columns[0].cardIds.append("card-abc123")
    new_board.cards["card-abc123"] = Card(id="card-abc123", title="New task", details="")
    with patch("routers.chat.call_ai_structured") as mock_ai:
        mock_ai.return_value = AIResponse(message="Added a card.", board_update=new_board)
        res = client.post(
            "/api/chat",
            json={"history": [], "user_message": "Add a task"},
            headers=auth_headers,
        )
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "Added a card."
    assert data["board_update"] is not None
    assert data["board_update"]["cards"]["card-abc123"]["title"] == "New task"


def test_chat_passes_board_and_history_to_ai(client, auth_headers):
    with patch("routers.chat.call_ai_structured") as mock_ai:
        mock_ai.return_value = AIResponse(message="Got it.", board_update=None)
        client.post(
            "/api/chat",
            json={
                "history": [{"role": "user", "content": "Earlier message"}],
                "user_message": "Current message",
            },
            headers=auth_headers,
        )
    mock_ai.assert_called_once()
    board_arg, messages_arg = mock_ai.call_args.args
    assert isinstance(board_arg, BoardData)
    assert len(messages_arg) == 2  # 1 history + 1 new user message
    assert messages_arg[-1].role == "user"
    assert messages_arg[-1].content == "Current message"


def test_chat_requires_auth(client):
    res = client.post("/api/chat", json={"history": [], "user_message": "Hello"})
    assert res.status_code == 422  # missing Authorization header
