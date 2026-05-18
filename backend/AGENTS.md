# Backend — Code Description

## Overview

A FastAPI Python backend served on port 8000. It will serve the statically-built Next.js frontend and expose a REST API. For Part 2 it is a hello-world skeleton; subsequent parts add auth, database, and AI endpoints.

## Tech stack

- Python 3.12
- FastAPI — web framework
- uvicorn[standard] — ASGI server
- uv — package manager (used in Docker)
- aiosqlite — async SQLite driver (added in Part 6)
- httpx — HTTP client for OpenRouter calls (added in Part 8)

## File structure

```
backend/
  main.py          FastAPI app instance; route definitions
  pyproject.toml   Project metadata and dependencies (uv-compatible)
  database.py      DB init, connection helper (added in Part 6)
  models.py        Pydantic request/response models (added in Part 6)
  ai.py            OpenRouter client (added in Part 8)
  routers/
    auth.py        Login / logout endpoints (added in Part 4)
    board.py       GET /api/board, PUT /api/board (added in Part 6)
    columns.py     PATCH /api/columns/{id} (added in Part 6)
    cards.py       POST/PATCH/DELETE /api/cards (added in Part 6)
    chat.py        POST /api/chat (added in Part 9)
  tests/
    test_auth.py
    test_board.py
    test_cards.py
    test_columns.py
    test_chat.py
```

## API routes (current)

| Method | Path         | Auth | Description                     |
|--------|-------------|------|---------------------------------|
| GET    | /            | No   | Hello-world HTML (Part 2 stub)  |
| GET    | /api/hello   | No   | Returns `{"message": "ok"}`     |

Additional routes are added in Parts 4, 6, 8, and 9.

## Running locally (without Docker)

```sh
cd backend
uv run uvicorn main:app --reload
```

## Environment variables

| Variable           | Required from | Description                    |
|--------------------|---------------|--------------------------------|
| OPENROUTER_API_KEY | Part 8        | API key for OpenRouter calls   |

Variables are loaded from `.env` in the project root when running via Docker Compose.
