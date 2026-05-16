import sqlite3
from datetime import datetime

from app.models.domain import Conversation


def insert(conn: sqlite3.Connection, conv: Conversation) -> None:
    conn.execute(
        "INSERT INTO conversations(id, type, created_at) VALUES (?, ?, ?)",
        (conv.id, conv.type, conv.created_at.isoformat()),
    )
    conn.executemany(
        "INSERT INTO conversation_participants(conversation_id, user_id) VALUES (?, ?)",
        [(conv.id, uid) for uid in conv.participant_ids],
    )


def get(conn: sqlite3.Connection, conv_id: str) -> Conversation | None:
    row = conn.execute(
        "SELECT id, type, created_at FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    if not row:
        return None
    participants = tuple(
        r["user_id"]
        for r in conn.execute(
            "SELECT user_id FROM conversation_participants WHERE conversation_id = ?",
            (conv_id,),
        ).fetchall()
    )
    return Conversation(
        id=row["id"],
        type=row["type"],
        participant_ids=participants,
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def find_direct_between(
    conn: sqlite3.Connection, user_a: str, user_b: str
) -> str | None:
    row = conn.execute(
        """
        SELECT c.id
        FROM conversations c
        JOIN conversation_participants p1 ON p1.conversation_id = c.id AND p1.user_id = ?
        JOIN conversation_participants p2 ON p2.conversation_id = c.id AND p2.user_id = ?
        WHERE c.type = 'direct'
        LIMIT 1
        """,
        (user_a, user_b),
    ).fetchone()
    return row["id"] if row else None


def is_participant(conn: sqlite3.Connection, conv_id: str, user_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM conversation_participants WHERE conversation_id = ? AND user_id = ?",
        (conv_id, user_id),
    ).fetchone()
    return row is not None
