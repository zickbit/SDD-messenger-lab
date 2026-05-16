import sqlite3
from datetime import datetime

from app.models.domain import Message


def _row_to_message(row: sqlite3.Row) -> Message:
    return Message(
        id=row["id"],
        conversation_id=row["conversation_id"],
        sender_id=row["sender_id"],
        text=row["text"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def insert(conn: sqlite3.Connection, msg: Message) -> None:
    conn.execute(
        """
        INSERT INTO messages(id, conversation_id, sender_id, text, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (msg.id, msg.conversation_id, msg.sender_id, msg.text,
         msg.created_at.isoformat()),
    )


def list_by_conversation(
    conn: sqlite3.Connection,
    conv_id: str,
    limit: int,
    before: datetime | None,
) -> list[Message]:
    if before is None:
        rows = conn.execute(
            """
            SELECT id, conversation_id, sender_id, text, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (conv_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, conversation_id, sender_id, text, created_at
            FROM messages
            WHERE conversation_id = ? AND created_at < ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (conv_id, before.isoformat(), limit),
        ).fetchall()
    return [_row_to_message(r) for r in rows]


def _escape_fts(q: str) -> str:
    """Wrap user input as a single phrase for FTS5 MATCH.

    Internal double quotes are doubled, then the whole thing is wrapped
    in double quotes. This neutralizes FTS operators from untrusted input.
    """
    return '"' + q.replace('"', '""') + '"'


def search(
    conn: sqlite3.Connection,
    q: str,
    conversation_id: str | None,
    sender_id: str | None,
    limit: int,
    offset: int,
) -> tuple[list[tuple[Message, float]], int]:
    match = _escape_fts(q)

    base_from = (
        "FROM messages_fts f "
        "JOIN messages m ON m.rowid = f.rowid "
        "WHERE f.text MATCH ? "
    )
    args: list = [match]

    if conversation_id is not None:
        base_from += "AND m.conversation_id = ? "
        args.append(conversation_id)
    if sender_id is not None:
        base_from += "AND m.sender_id = ? "
        args.append(sender_id)

    count_sql = "SELECT COUNT(*) AS total " + base_from
    total = conn.execute(count_sql, args).fetchone()["total"]

    select_sql = (
        "SELECT m.id, m.conversation_id, m.sender_id, m.text, m.created_at, "
        "bm25(messages_fts) AS rank "
        + base_from
        + "ORDER BY rank LIMIT ? OFFSET ?"
    )
    rows = conn.execute(select_sql, args + [limit, offset]).fetchall()
    results = [(_row_to_message(r), r["rank"]) for r in rows]
    return results, total
