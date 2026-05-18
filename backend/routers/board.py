import sqlite3

from fastapi import APIRouter, Depends

from database import get_db
from models import BoardData, Card, Column
from routers.auth import get_token

router = APIRouter()

# MVP: single hardcoded user
_USER_ID = "user-1"


def load_board(db: sqlite3.Connection) -> BoardData:
    board = db.execute(
        "SELECT id FROM boards WHERE user_id = ?", (_USER_ID,)
    ).fetchone()
    if not board:
        return BoardData(columns=[], cards={})

    board_id = board["id"]
    cols = db.execute(
        "SELECT id, title FROM columns WHERE board_id = ? ORDER BY position",
        (board_id,),
    ).fetchall()

    all_cards = db.execute(
        """
        SELECT c.id, c.title, c.details, c.column_id
        FROM cards c
        JOIN columns col ON col.id = c.column_id
        WHERE col.board_id = ?
        ORDER BY c.column_id, c.position
        """,
        (board_id,),
    ).fetchall()

    cards_by_col: dict[str, list[str]] = {col["id"]: [] for col in cols}
    cards: dict[str, Card] = {}

    for row in all_cards:
        card = Card(id=row["id"], title=row["title"], details=row["details"])
        cards[card.id] = card
        cards_by_col[row["column_id"]].append(card.id)

    columns = [
        Column(id=col["id"], title=col["title"], cardIds=cards_by_col[col["id"]])
        for col in cols
    ]

    return BoardData(columns=columns, cards=cards)


@router.get("/api/board")
def get_board(
    token: str = Depends(get_token),
    db: sqlite3.Connection = Depends(get_db),
) -> BoardData:
    return load_board(db)


@router.put("/api/board")
def put_board(
    body: BoardData,
    token: str = Depends(get_token),
    db: sqlite3.Connection = Depends(get_db),
) -> BoardData:
    board = db.execute(
        "SELECT id FROM boards WHERE user_id = ?", (_USER_ID,)
    ).fetchone()
    board_id = board["id"]

    col_ids = [
        r["id"]
        for r in db.execute(
            "SELECT id FROM columns WHERE board_id = ?", (board_id,)
        ).fetchall()
    ]
    if col_ids:
        db.execute(
            f"DELETE FROM cards WHERE column_id IN ({','.join('?' * len(col_ids))})",
            col_ids,
        )
    db.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))

    for pos, col in enumerate(body.columns):
        db.execute(
            "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
            (col.id, board_id, col.title, pos),
        )
        for card_pos, card_id in enumerate(col.cardIds):
            card = body.cards.get(card_id)
            if card:
                db.execute(
                    "INSERT INTO cards (id, column_id, title, details, position)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (card.id, col.id, card.title, card.details, card_pos),
                )

    db.commit()
    return load_board(db)
