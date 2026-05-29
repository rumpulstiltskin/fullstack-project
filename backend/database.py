import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Generator

DB_PATH = Path(os.environ.get("DB_PATH", str(Path(__file__).parent / "kanban.db")))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id       TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS boards (
    id      TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS columns (
    id       TEXT PRIMARY KEY,
    board_id TEXT NOT NULL REFERENCES boards(id),
    title    TEXT NOT NULL,
    position INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cards (
    id        TEXT PRIMARY KEY,
    column_id TEXT NOT NULL REFERENCES columns(id),
    title     TEXT NOT NULL,
    details   TEXT NOT NULL DEFAULT '',
    position  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_token TEXT NOT NULL,
    role          TEXT NOT NULL,
    content       TEXT NOT NULL
)
"""

_SEED_COLUMNS = [
    ("col-backlog", "Backlog"),
    ("col-discovery", "Discovery"),
    ("col-progress", "In Progress"),
    ("col-review", "Review"),
    ("col-done", "Done"),
]

_SEED_CARDS = [
    ("card-1", "col-backlog", "Align roadmap themes", "Draft quarterly themes with impact statements and metrics.", 0),
    ("card-2", "col-backlog", "Gather customer signals", "Review support tags, sales notes, and churn feedback.", 1),
    ("card-3", "col-discovery", "Prototype analytics view", "Sketch initial dashboard layout and key drill-downs.", 0),
    ("card-4", "col-progress", "Refine status language", "Standardize column labels and tone across the board.", 0),
    ("card-5", "col-progress", "Design card layout", "Add hierarchy and spacing for scanning dense lists.", 1),
    ("card-6", "col-review", "QA micro-interactions", "Verify hover, focus, and loading states.", 0),
    ("card-7", "col-done", "Ship marketing page", "Final copy approved and asset pack delivered.", 0),
    ("card-8", "col-done", "Close onboarding sprint", "Document release notes and share internally.", 1),
]

_HASH_ITERATIONS = 260_000
_HASH_ALG = "sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        _HASH_ALG,
        password.encode(),
        salt.encode(),
        _HASH_ITERATIONS,
    ).hex()
    return f"{salt}:{digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
    except ValueError:
        return False
    expected = hashlib.pbkdf2_hmac(
        _HASH_ALG,
        password.encode(),
        salt.encode(),
        _HASH_ITERATIONS,
    ).hex()
    return hmac.compare_digest(expected, digest)


def open_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    for stmt in _SCHEMA.split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)
    conn.commit()


def seed(conn: sqlite3.Connection) -> None:
    username = os.environ.get("APP_USERNAME", "user")
    if conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
        return
    password = os.environ.get("APP_PASSWORD", "password")
    conn.execute(
        "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
        ("user-1", username, hash_password(password)),
    )
    conn.execute(
        "INSERT INTO boards (id, user_id, name) VALUES (?, ?, ?)",
        ("board-1", "user-1", "My Board"),
    )
    for i, (col_id, title) in enumerate(_SEED_COLUMNS):
        conn.execute(
            "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
            (col_id, "board-1", title, i),
        )
    for card_id, col_id, title, details, position in _SEED_CARDS:
        conn.execute(
            "INSERT INTO cards (id, column_id, title, details, position) VALUES (?, ?, ?, ?, ?)",
            (card_id, col_id, title, details, position),
        )
    conn.commit()


def init_db() -> None:
    conn = open_db(DB_PATH)
    apply_schema(conn)
    seed(conn)
    conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = open_db(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
