import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_db
from app.api.schemas import (
    ConversationResponse,
    CreateConversationRequest,
    HistoryResponse,
    MessageResponse,
)
from app.services import conversation_service, message_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse,
             status_code=status.HTTP_201_CREATED)
def create_conversation(
    req: CreateConversationRequest, conn: sqlite3.Connection = Depends(get_db)
):
    conv = conversation_service.create_direct(conn, req.participantIds)
    return ConversationResponse.from_domain(conv)


@router.get("/{conversation_id}/messages", response_model=HistoryResponse)
def get_history(
    conversation_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    before: datetime | None = Query(default=None),
    conn: sqlite3.Connection = Depends(get_db),
):
    msgs, next_before = message_service.history(conn, conversation_id, limit, before)
    return HistoryResponse(
        messages=[MessageResponse.from_domain(m) for m in msgs],
        nextBefore=next_before,
    )
