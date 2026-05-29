import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from database import get_db, verify_password
from rate_limit import check as rate_check

router = APIRouter()

_SESSION_COOKIE = "session"
_SESSION_DAYS = 7


def get_token(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> str:
    token = request.cookies.get(_SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    row = db.execute(
        "SELECT user_id, expires_at FROM sessions WHERE token = ?", (token,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired")
    return token


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/api/auth/login")
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_check(f"login:{client_ip}", max_calls=5, window_secs=60.0):
        raise HTTPException(status_code=429, detail="Too many login attempts")

    username = os.environ.get("APP_USERNAME", "user")
    user_row = db.execute(
        "SELECT id, password FROM users WHERE username = ?", (username,)
    ).fetchone()

    if (
        not user_row
        or body.username != username
        or not verify_password(body.password, user_row["password"])
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = secrets.token_hex(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(days=_SESSION_DAYS)).isoformat()

    with db:
        db.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_row["id"], expires_at),
        )

    response.set_cookie(
        key=_SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=_SESSION_DAYS * 86400,
    )
    return {"ok": True}


@router.post("/api/auth/logout")
def logout(
    response: Response,
    token: str = Depends(get_token),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    with db:
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
    response.delete_cookie(key=_SESSION_COOKIE)
    return {"ok": True}
