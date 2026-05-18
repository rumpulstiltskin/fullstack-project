# Project Management MVP — Detailed Plan

## Part 1: Plan

### Goal
Produce planning documents and get user approval before any implementation begins.

### Checklist
- [x] Enrich this document with per-part checklists, tests, and success criteria
- [x] Create `frontend/AGENTS.md` describing the existing frontend code
- [x] User reviews and approves this plan

### Success criteria
- User has approved this document before Part 2 begins

---

## Part 2: Scaffolding

### Goal
A Docker container runs locally. `http://localhost:8000/` returns a static hello-world HTML page. `http://localhost:8000/api/hello` returns `{"message": "ok"}`. Start and stop scripts work on Mac, PC, and Linux.

### Checklist
- [x] Create `backend/main.py` — FastAPI app; `GET /` returns minimal HTML; `GET /api/hello` returns `{"message": "ok"}`
- [x] Create `backend/pyproject.toml` — declares `fastapi` and `uvicorn[standard]` as dependencies; uses uv as the package manager
- [x] Create `Dockerfile` — two stages: `node:20-alpine` build stage (stubbed for now, will be used in Part 3); `python:3.12-slim` runtime stage that installs uv, installs dependencies, copies backend, runs `uvicorn` on port 8000
- [x] Create `docker-compose.yml` — single service; mounts `.env`; exposes port 8000
- [x] Create `scripts/start.sh` and `scripts/stop.sh` — Mac/Linux; `docker compose up --build -d` and `docker compose down`
- [x] Create `scripts/start.bat` and `scripts/stop.bat` — Windows equivalents
- [x] Update `backend/AGENTS.md` with a description of the backend structure

### Tests / success criteria
- `docker compose up --build` completes with no errors
- `curl http://localhost:8000/` returns an HTML response
- `curl http://localhost:8000/api/hello` returns `{"message": "ok"}`
- `scripts/start.sh` (or `.bat`) brings the container up
- `scripts/stop.sh` (or `.bat`) brings it down cleanly

---

## Part 3: Add in Frontend

### Goal
The Next.js app is statically built inside Docker and served by FastAPI at `/`. The Kanban board is visible and fully interactive in the containerised environment.

### Checklist
- [x] Set `output: 'export'` in `frontend/next.config.ts` so Next.js produces a static `out/` directory
- [x] Add the node build stage to `Dockerfile`: install dependencies with npm ci, run `next build`, copy `out/` into the Python stage
- [x] Serve static files via a `/{full_path:path}` catch-all route using `FileResponse` (not `StaticFiles` — avoids the `aiofiles` dependency); returns `index.html` for unknown paths so client-side routing works
- [x] Verify drag-and-drop works end-to-end in the containerised build (no SSR/hydration mismatch)
- [x] Update `frontend/playwright.config.ts` base URL to `http://localhost:8000`
- [x] All existing Vitest unit tests pass unchanged
- [x] All existing Playwright E2E tests pass against the container

### Tests / success criteria
- `http://localhost:8000/` serves the Kanban board
- `vitest run` — all unit tests pass
- `playwright test` — all three E2E tests pass against `localhost:8000`
- No browser console errors on load

---

## Part 4: Fake User Sign-in

### Goal
Unauthenticated visits to `/` show a login page. Credentials `user` / `password` grant access to the Kanban board. A logout button returns the user to the login page.

### Checklist

**Backend**
- [x] Add `POST /api/auth/login` — accepts `{ username, password }`; validates against hardcoded values; returns `{ token: "<random uuid>" }` and stores the token in an in-memory set; returns 401 on bad credentials
- [x] Add `POST /api/auth/logout` — removes the token from the in-memory set; returns 200
- [x] Add an auth middleware / dependency that reads `Authorization: Bearer <token>` on protected routes and returns 401 if missing or invalid

**Frontend**
- [x] Create `frontend/src/lib/auth.ts` — `login(user, pass)` posts to `/api/auth/login` and stores the token in `localStorage`; `logout()` clears localStorage and calls `/api/auth/logout`; `getToken()` returns the stored token or null
- [x] Create `frontend/src/components/LoginPage.tsx` — form with username and password inputs; submit calls `login()`; shows an error message on 401; on success sets authenticated state; matches existing color scheme
- [x] Update `frontend/src/app/page.tsx` — check `getToken()` on mount; render `<LoginPage>` if not authenticated, `<KanbanBoard>` otherwise
- [x] Add a logout button to the `KanbanBoard` header that calls `logout()` and resets the auth state

**Tests**
- [x] Backend: 7 tests covering login success/failure, logout, token invalidation, missing/invalid token
- [x] E2E test: visit `/` → see login form → enter correct credentials → see board → click logout → see login form again
- [x] E2E test: enter wrong credentials → see error message

### Success criteria
- Unauthenticated visit shows login form, not the board
- Correct credentials show the board
- Incorrect credentials show an error message (no credentials leaked in the message)
- Logout works and the token is invalidated server-side
- All new unit and E2E tests pass

---

## Part 5: Database Schema

### Goal
Agree on a SQLite schema that supports the MVP and is extensible for multiple users and boards in future.

### Checklist
- [x] Write `docs/DATABASE.md` with the proposed schema, column types, and constraints
- [x] Present schema to user and get sign-off

### Proposed schema

```sql
CREATE TABLE users (
    id       TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL          -- plaintext for MVP (hardcoded); hash in future
);

CREATE TABLE boards (
    id      TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name    TEXT NOT NULL
);

CREATE TABLE columns (
    id       TEXT PRIMARY KEY,
    board_id TEXT NOT NULL REFERENCES boards(id),
    title    TEXT NOT NULL,
    position INTEGER NOT NULL
);

CREATE TABLE cards (
    id        TEXT PRIMARY KEY,
    column_id TEXT NOT NULL REFERENCES columns(id),
    title     TEXT NOT NULL,
    details   TEXT NOT NULL DEFAULT '',
    position  INTEGER NOT NULL
);
```

### Success criteria
- User approves schema in `docs/DATABASE.md` before Part 6 begins

---

## Part 6: Backend API

### Goal
Full CRUD API for boards, columns, and cards backed by SQLite. The database is created automatically on first run and seeded with the hardcoded user and a default board.

### Checklist
- [x] Create `backend/database.py` — `init_db()` creates tables + seeds user/board/columns; `get_db()` yields a sqlite3 connection; `apply_schema()` and `seed()` are testable separately
- [x] Create `backend/models.py` — `Card`, `Column`, `BoardData` Pydantic models matching the frontend types
- [x] Create `backend/routers/board.py` — `GET /api/board` and `PUT /api/board` (full-replace); granular card/column endpoints omitted — PUT board covers all mutations
- [x] All board routes protected by `get_token` dependency from auth router
- [x] Write `backend/tests/conftest.py` — `client` fixture with temp DB + `get_db` override; `auth_headers` fixture
- [x] Write `backend/tests/test_board.py` — GET returns seeded columns, PUT round-trips, auth required
- [x] All 11 backend tests pass (`pytest -v`)

### Success criteria
- `pytest backend/tests/` — all tests pass
- DB file is created on first container start if it doesn't exist
- All CRUD operations round-trip correctly
- Unauthenticated requests to protected routes return 401

---

## Part 7: Frontend + Backend Integration

### Goal
The frontend reads its initial board state from the API and writes every mutation back. Board state persists across browser refreshes.

### Checklist
- [x] Create `frontend/src/lib/api.ts` — `getBoard()` and `putBoard()`; attaches `Authorization: Bearer <token>` from `getToken()`; throws on non-2xx
- [x] Update `KanbanBoard.tsx`:
  - `useState<BoardData | null>(null)` with `isLoading` and `error` states
  - `useEffect` on mount calls `getBoard()` and sets state; shows "Loading board..." or error message
  - `boardRef` tracks latest board state; `saveTimerRef` holds a pending debounce timer
  - Rename: 500ms debounce — `boardRef` updated immediately, `putBoard(boardRef.current)` called on timer expiry (avoids stale closure across rapid keystrokes)
  - All other mutations (drag, add card, delete card): `putBoard` called immediately, fire-and-forget (errors silently ignored — board state is already applied locally)
- [x] Update `backend/database.py` seed: column IDs changed from `col-1..col-5` to semantic IDs (`col-backlog`, `col-discovery`, `col-progress`, `col-review`, `col-done`) to match the frontend data model and E2E `data-testid` selectors
- [x] Update unit tests for `KanbanBoard` to mock `@/lib/api` (use `vi.mock`); switch to `findAllByTestId` for async board load
- [x] Update E2E tests:
  - Add card → refresh page → card is still present (uses `waitForResponse` on PUT before reload)
  - Drag card to new column → refresh → card is in new column

### Design decisions
- `putBoard` is fire-and-forget: mutations are applied optimistically to local state and the PUT result is not used to update state. This keeps the UI snappy and avoids a round-trip on every interaction.
- The board DB starts with 5 empty columns (no seed cards). The frontend no longer uses `initialData` from `kanban.ts` for the live board.

### Success criteria
- Board state persists across browser refresh
- All existing and new unit tests pass (6 unit, 11 backend, 8 E2E)
- All E2E tests pass

---

## Part 8: AI Connectivity

### Goal
The backend can reach OpenRouter. A test endpoint confirms a live response.

### Checklist
- [x] Move `httpx` from dev to runtime dependencies in `pyproject.toml`; update Dockerfile install line
- [x] Create `backend/ai.py` — `call_ai(messages: list[dict]) -> str`; POSTs to OpenRouter with model `openai/gpt-oss-120b:free`; reads `OPENROUTER_API_KEY` from environment at call time; raises `RuntimeError` if key missing, `httpx.HTTPStatusError` on bad response
- [x] Create `backend/routers/ai.py` — `GET /api/ai/test` (auth-protected); calls `call_ai` with "What is 2+2?"; returns `{ response: str }`; maps `RuntimeError` to 503
- [x] Update `backend/main.py` — include `ai_router`; log a warning at startup if `OPENROUTER_API_KEY` is not set
- [x] Verified live: `GET /api/ai/test` returns a response containing "4"

---

## Part 9: Structured AI Responses

### Goal
Every AI call receives the current board state and conversation history. The AI responds with a user-facing message and an optional full board update.

### Checklist
- [x] Add `ChatMessage`, `ChatRequest`, `AIResponse` to `backend/models.py`
- [x] Update `backend/ai.py` — add `call_ai_structured(board, messages) -> AIResponse`; builds a system prompt embedding the board as JSON + strict JSON-only response instructions; strips markdown code fences before parsing; validates with Pydantic; raises `RuntimeError` on bad JSON
- [x] Rename `_load_board` → `load_board` in `backend/routers/board.py` so the chat router can import it
- [x] Create `backend/routers/chat.py` — `POST /api/chat` (auth-protected): loads current board, appends user message to history, calls `call_ai_structured`, maps `RuntimeError` to 502
- [x] Include `chat_router` in `backend/main.py`
- [x] Write `backend/tests/test_chat.py` — 4 tests: message-only response, board_update response, correct args passed to AI, auth required

### Design decisions
- `call_ai_structured` reuses `call_ai` internally, passing a system message as the first element of the messages list
- The system prompt includes the full board JSON and instructs the model to respond with ONLY a JSON object — no preamble, no markdown
- `_extract_json` strips ` ```json ``` ` code fences before parsing, as some models wrap responses in them
- The chat endpoint does not persist `board_update` to the DB — that is the frontend's responsibility (Part 10)

### Success criteria
- `POST /api/chat` with a simple question returns `{ message: "...", board_update: null }` ✓ verified live
- `POST /api/chat` asking to add a card returns a valid `board_update` with all 5 columns and the new card ✓ verified live
- All 15 backend tests pass ✓

---

## Part 10: AI Chat Sidebar

### Goal
A sidebar widget in the UI allows the user to chat with the AI. When the AI returns a board update, the board refreshes automatically without a page reload.

### Checklist
- [x] Create `frontend/src/lib/chat.ts` — `sendMessage(history: ChatMessage[], userMessage: string) -> Promise<AIResponse>`; posts to `/api/chat`
- [x] Create `frontend/src/components/AISidebar.tsx`:
  - Collapsible panel anchored to the right side of the screen
  - Scrollable message list showing user and assistant turns
  - Text input and submit button at the bottom
  - Typing indicator (simple animated dots) while awaiting the response
  - Auto-scrolls to the latest message
  - Styled using the existing CSS custom properties and color scheme
- [x] Update `KanbanBoard.tsx`:
  - Add sidebar open/close toggle state
  - Add a toggle button in the header
  - Pass a `onBoardUpdate` callback into `AISidebar`; when `board_update` is non-null, call `setBoard` with the new state and call `PUT /api/board` to persist it
- [x] Unit tests for `chat.ts`: mocked fetch; verifies request shape and response parsing
- [x] Unit test for `AISidebar`: renders message list; sends message on submit; shows typing indicator
- [x] E2E test: open sidebar → type "Add a card called Test Card to Backlog" → send → verify card appears in Backlog column without a page reload

### Design decisions
- `scrollIntoView` uses double optional chain (`?.scrollIntoView?.()`) for jsdom compatibility in unit tests
- `data-testid="thinking-indicator"` on the animated dots container for testability
- E2E text assertions use `.first()` throughout to handle DB accumulation across repeated test runs (persistent SQLite keeps all cards from prior runs)
- AI `waitForResponse` timeout set to 60s; free OpenRouter model latency can exceed 30s

### Success criteria
- Sidebar opens and closes via the header toggle
- Sending a message shows the AI's reply in the sidebar
- When the AI returns a board update, the board updates immediately
- Board update is persisted (refresh still shows the change)
- All new unit and E2E tests pass
