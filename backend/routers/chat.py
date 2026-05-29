import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ai import call_ai_structured
from database import get_db
from models import AIResponse, ChatMessage, ChatRequest
from rate_limit import check as rate_check
from routers.auth import get_token
from routers.board import load_board

router = APIRouter()


@router.post("/api/chat")
def chat(
    body: ChatRequest,
    token: str = Depends(get_token),
    db: sqlite3.Connection = Depends(get_db),
) -> AIResponse:
    if not rate_check(f"chat:{token}", max_calls=30, window_secs=60.0):
        raise HTTPException(status_code=429, detail="Too many requests")

    board = load_board(db)

    rows = db.execute(
        "SELECT role, content FROM chat_history WHERE session_token = ? ORDER BY id",
        (token,),
    ).fetchall()
    history = [ChatMessage(role=row["role"], content=row["content"]) for row in rows]

    messages = history + [ChatMessage(role="user", content=body.user_message)]

    try:
        result = call_ai_structured(board, messages)
    except RuntimeError:
        raise HTTPException(status_code=502, detail="AI service unavailable")

    with db:
        db.execute(
            "INSERT INTO chat_history (session_token, role, content) VALUES (?, ?, ?)",
            (token, "user", body.user_message),
        )
        db.execute(
            "INSERT INTO chat_history (session_token, role, content) VALUES (?, ?, ?)",
            (token, "assistant", result.message),
        )

    return result
