import sqlite3
from pathlib import Path
from typing import Generator

DB_PATH = Path(__file__).parent / "kanban.db"

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
"""

_SEED_COLUMNS = [
    ("col-backlog", "Backlog"),
    ("col-discovery", "Discovery"),
    ("col-progress", "In Progress"),
    ("col-review", "Review"),
    ("col-done", "Done"),
]


def _open(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def seed(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT id FROM users WHERE username = 'user'").fetchone():
        return
    conn.execute(
        "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
        ("user-1", "user", "password"),
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
    conn.commit()


def init_db() -> None:
    conn = _open(DB_PATH)
    apply_schema(conn)
    seed(conn)
    conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _open(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
