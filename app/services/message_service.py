import sqlite3
import uuid
from datetime import datetime

from app.models.domain import Message
from app.services.errors import (
    ConversationNotFoundError,
    EmptyMessageError,
    NotAParticipantError,
    UserNotFoundError,
)
from app.storage import conversation_repo, message_repo, user_repo


def send(
    conn: sqlite3.Connection, conversation_id: str, sender_id: str, text: str
) -> Message:
    text = text.strip()
    if not text:
        raise EmptyMessageError()

    if not user_repo.exists(conn, sender_id):
        raise UserNotFoundError(sender_id)

    if conversation_repo.get(conn, conversation_id) is None:
        raise ConversationNotFoundError(conversation_id)

    if not conversation_repo.is_participant(conn, conversation_id, sender_id):
        raise NotAParticipantError()

    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender_id=sender_id,
        text=text,
        created_at=user_repo.now_utc(),
    )
    message_repo.insert(conn, msg)
    return msg


def history(
    conn: sqlite3.Connection,
    conversation_id: str,
    limit: int,
    before: datetime | None,
) -> tuple[list[Message], datetime | None]:
    if conversation_repo.get(conn, conversation_id) is None:
        raise ConversationNotFoundError(conversation_id)

    msgs = message_repo.list_by_conversation(conn, conversation_id, limit, before)
    next_before = msgs[-1].created_at if len(msgs) == limit else None
    return msgs, next_before
