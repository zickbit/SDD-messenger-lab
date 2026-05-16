import sqlite3

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_db
from app.api.schemas import (
    MessageResponse,
    SearchResponse,
    SearchResultItem,
    SendMessageRequest,
)
from app.services import message_service, search_service

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageResponse,
             status_code=status.HTTP_201_CREATED)
def send_message(
    req: SendMessageRequest, conn: sqlite3.Connection = Depends(get_db)
):
    msg = message_service.send(conn, req.conversationId, req.senderId, req.text)
    return MessageResponse.from_domain(msg)


@router.get("/search", response_model=SearchResponse)
def search_messages(
    q: str = Query(min_length=1),
    conversationId: str | None = Query(default=None),
    senderId: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    conn: sqlite3.Connection = Depends(get_db),
):
    results, total = search_service.search(
        conn, q, conversationId, senderId, limit, offset
    )
    items = [
        SearchResultItem(
            id=m.id,
            conversationId=m.conversation_id,
            senderId=m.sender_id,
            text=m.text,
            createdAt=m.created_at,
            rank=rank,
        )
        for m, rank in results
    ]
    return SearchResponse(
        query=q, total=total, limit=limit, offset=offset, results=items
    )
