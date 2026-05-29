# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A full-stack Kanban board MVP with AI chat integration. The frontend is a Next.js static export served by a FastAPI backend. The AI chat can read and mutate board state via structured responses from OpenRouter.

## Development Commands

### Docker (primary workflow)
```bash
docker compose up --build    # Build and start the app at http://localhost:8000
docker compose down          # Stop
scripts/start.sh             # Convenience start
scripts/stop.sh              # Convenience stop
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Dev server (port 3000)
npm run build        # Static export to frontend/out/
npm run lint         # ESLint
npm run test:unit    # Vitest unit tests
npm run test:e2e     # Playwright E2E tests (requires running app at localhost:8000)
npm run test:all     # Both suites
```

### Backend
```bash
cd backend
uv run uvicorn main:app --reload   # Dev server (port 8000)
uv run pytest -v                   # All tests
uv run pytest tests/test_auth.py   # Single test file
```

## Architecture

### Request Flow
1. Browser loads Next.js static build served from FastAPI's `/static`
2. Frontend fetches board state via `GET /api/board` on mount
3. User interactions update local React state + call `PUT /api/board` (fire-and-forget)
4. AI chat posts to `POST /api/chat`, which calls OpenRouter and returns `{ message, board_update }`
5. Non-null `board_update` is applied to local state and persisted via `PUT /api/board`

### Backend (`backend/`)
- **`main.py`** — FastAPI app entry point; registers routers; lifespan hook initializes SQLite
- **`database.py`** — SQLite connection, schema creation, seed data (hardcoded user + 1 board + 5 empty columns)
- **`models.py`** — Pydantic models: `Card`, `Column`, `BoardData`, `ChatMessage`, `ChatRequest`, `AIResponse`
- **`ai.py`** — OpenRouter client (`call_ai`, `call_ai_structured`)
- **`routers/auth.py`** — `POST /api/auth/login`, `POST /api/auth/logout`; token validation
- **`routers/board.py`** — `GET /api/board`, `PUT /api/board`
- **`routers/chat.py`** — `POST /api/chat`; structured AI response that can include board mutations
- **`tests/`** — pytest suite (`conftest.py`, `test_auth.py`, `test_board.py`, `test_chat.py`)

### Frontend (`frontend/src/`)
- **`app/`** — Next.js app router (layout, root page)
- **`components/KanbanBoard.tsx`** — Root board component; owns all board state; coordinates API and AI sidebar
- **`components/KanbanColumn.tsx`** — Droppable column (@dnd-kit)
- **`components/KanbanCard.tsx`** — Sortable card with edit/delete
- **`components/AISidebar.tsx`** — Collapsible AI chat panel
- **`components/AuthWrapper.tsx`** / **`LoginPage.tsx`** — Auth flow
- **`lib/api.ts`** — `getBoard`, `putBoard`; attaches auth header
- **`lib/chat.ts`** — `sendMessage` to AI endpoint
- **`lib/auth.ts`** — Login/logout; token stored in localStorage
- **`lib/kanban.ts`** — Data types, `moveCard` logic, `createId`
- **`tests/`** — Vitest setup; `../tests/` — Playwright E2E

### Data Model
SQLite tables: `users`, `boards`, `columns`, `cards`. Foreign keys enforced via `PRAGMA foreign_keys = ON`. MVP uses a single hardcoded user (`user`/`password`) and one board.

### Environment
Requires `OPENROUTER_API_KEY` in `.env` for AI chat features. The backend reads it at startup; tests mock it via `conftest.py`.

## Key Constraints
- Next.js is configured for **static export** (`output: 'export'`). No server-side rendering or API routes in the frontend.
- Column structure is fixed at 5 columns (Backlog, Discovery, In Progress, Review, Done). Columns can be renamed but not added/removed.
- The Dockerfile does a multi-stage build: Node 20 builds the frontend, Python 3.12 serves it.
- Path alias `@/*` maps to `frontend/src/*`.
