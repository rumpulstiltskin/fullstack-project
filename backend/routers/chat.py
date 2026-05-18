import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ai import call_ai_structured
from database import get_db
from models import AIResponse, ChatMessage, ChatRequest
from routers.auth import get_token
from routers.board import load_board

router = APIRouter()


@router.post("/api/chat")
def chat(
    body: ChatRequest,
    token: str = Depends(get_token),
    db: sqlite3.Connection = Depends(get_db),
) -> AIResponse:
    board = load_board(db)
    messages = body.history + [ChatMessage(role="user", content=body.user_message)]
    try:
        return call_ai_structured(board, messages)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
