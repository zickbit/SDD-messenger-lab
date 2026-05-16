import sqlite3

from app.models.domain import Message
from app.services.errors import InvalidSearchQueryError
from app.storage import message_repo


def search(
    conn: sqlite3.Connection,
    q: str,
    conversation_id: str | None,
    sender_id: str | None,
    limit: int,
    offset: int,
) -> tuple[list[tuple[Message, float]], int]:
    q = q.strip()
    if len(q) < 2:
        raise InvalidSearchQueryError()
    return message_repo.search(conn, q, conversation_id, sender_id, limit, offset)
