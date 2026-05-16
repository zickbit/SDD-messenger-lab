from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: str
    name: str
    created_at: datetime


@dataclass(frozen=True)
class Conversation:
    id: str
    type: str
    participant_ids: tuple[str, ...]
    created_at: datetime


@dataclass(frozen=True)
class Message:
    id: str
    conversation_id: str
    sender_id: str
    text: str
    created_at: datetime
