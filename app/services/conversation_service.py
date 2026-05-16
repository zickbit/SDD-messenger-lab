import sqlite3
import uuid

from app.models.domain import Conversation
from app.services.errors import (
    DirectConversationExistsError,
    InvalidParticipantsError,
    UserNotFoundError,
)
from app.storage import conversation_repo, user_repo


def create_direct(conn: sqlite3.Connection, participant_ids: list[str]) -> Conversation:
    if len(participant_ids) != 2:
        raise InvalidParticipantsError(
            "A direct conversation requires exactly 2 participants"
        )
    if participant_ids[0] == participant_ids[1]:
        raise InvalidParticipantsError("Participants must be distinct")

    for uid in participant_ids:
        if not user_repo.exists(conn, uid):
            raise UserNotFoundError(uid)

    existing = conversation_repo.find_direct_between(
        conn, participant_ids[0], participant_ids[1]
    )
    if existing:
        raise DirectConversationExistsError(existing)

    conv = Conversation(
        id=str(uuid.uuid4()),
        type="direct",
        participant_ids=tuple(participant_ids),
        created_at=user_repo.now_utc(),
    )
    conversation_repo.insert(conn, conv)
    return conv
