import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

router = APIRouter()

_tokens: set[str] = set()

_USERNAME = "user"
_PASSWORD = "password"


def get_token(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.removeprefix("Bearer ")
    if token not in _tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/api/auth/login")
def login(body: LoginRequest) -> dict:
    if body.username != _USERNAME or body.password != _PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = secrets.token_hex(32)
    _tokens.add(token)
    return {"token": token}


@router.post("/api/auth/logout")
def logout(token: str = Depends(get_token)) -> dict:
    _tokens.discard(token)
    return {"ok": True}
