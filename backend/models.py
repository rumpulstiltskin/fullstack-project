from typing import Literal

from pydantic import BaseModel, Field


class Card(BaseModel):
    id: str = Field(max_length=64)
    title: str = Field(max_length=200)
    details: str = Field(max_length=2000)


class Column(BaseModel):
    id: str = Field(max_length=64)
    title: str = Field(max_length=100)
    cardIds: list[str]


class BoardData(BaseModel):
    columns: list[Column]
    cards: dict[str, Card]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    user_message: str = Field(max_length=2000)


class AIResponse(BaseModel):
    message: str
    board_update: BoardData | None = None
