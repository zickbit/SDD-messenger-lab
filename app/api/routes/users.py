import sqlite3

from fastapi import APIRouter, Depends, status

from app.api.deps import get_db
from app.api.schemas import CreateUserRequest, UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(req: CreateUserRequest, conn: sqlite3.Connection = Depends(get_db)):
    user = user_service.create(conn, req.name)
    return UserResponse.from_domain(user)


@router.get("", response_model=list[UserResponse])
def list_users(conn: sqlite3.Connection = Depends(get_db)):
    return [UserResponse.from_domain(u) for u in user_service.list_all(conn)]
