import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

from database import init_db
from routers.ai import router as ai_router
from routers.auth import router as auth_router
from routers.board import router as board_router
from routers.chat import router as chat_router

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: StarletteRequest, call_next
    ) -> StarletteResponse:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY is not set — AI features will not work")
    init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.add_middleware(SecurityHeadersMiddleware)
app.include_router(auth_router)
app.include_router(board_router)
app.include_router(ai_router)
app.include_router(chat_router)

STATIC_DIR = Path(__file__).parent / "static"
_STATIC_RESOLVED = STATIC_DIR.resolve()


@app.get("/api/hello")
def hello() -> dict:
    return {"message": "ok"}


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str) -> FileResponse:
    candidate = (STATIC_DIR / full_path).resolve()
    if not candidate.is_relative_to(_STATIC_RESOLVED):
        return FileResponse(STATIC_DIR / "index.html")
    if candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(STATIC_DIR / "index.html")
