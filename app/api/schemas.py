from datetime import datetime

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: str
    name: str
    createdAt: datetime

    @classmethod
    def from_domain(cls, user) -> "UserResponse":
        return cls(id=user.id, name=user.name, createdAt=user.created_at)


class CreateConversationRequest(BaseModel):
    participantIds: list[str]


class ConversationResponse(BaseModel):
    id: str
    type: str
    participantIds: list[str]
    createdAt: datetime

    @classmethod
    def from_domain(cls, c) -> "ConversationResponse":
        return cls(
            id=c.id,
            type=c.type,
            participantIds=list(c.participant_ids),
            createdAt=c.created_at,
        )


class SendMessageRequest(BaseModel):
    conversationId: str
    senderId: str
    text: str


class MessageResponse(BaseModel):
    id: str
    conversationId: str
    senderId: str
    text: str
    createdAt: datetime

    @classmethod
    def from_domain(cls, m) -> "MessageResponse":
        return cls(
            id=m.id,
            conversationId=m.conversation_id,
            senderId=m.sender_id,
            text=m.text,
            createdAt=m.created_at,
        )


class HistoryResponse(BaseModel):
    messages: list[MessageResponse]
    nextBefore: datetime | None


class SearchResultItem(BaseModel):
    id: str
    conversationId: str
    senderId: str
    text: str
    createdAt: datetime
    rank: float


class SearchResponse(BaseModel):
    query: str
    total: int
    limit: int
    offset: int
    results: list[SearchResultItem]
