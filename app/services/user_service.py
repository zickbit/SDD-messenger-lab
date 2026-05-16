import sqlite3
import uuid

from app.models.domain import User
from app.services.errors import UserNameTakenError
from app.storage import user_repo


def create(conn: sqlite3.Connection, name: str) -> User:
    name = name.strip()
    if user_repo.find_by_name(conn, name) is not None:
        raise UserNameTakenError(name)
    user = User(id=str(uuid.uuid4()), name=name, created_at=user_repo.now_utc())
    user_repo.insert(conn, user)
    return user


def list_all(conn: sqlite3.Connection) -> list[User]:
    return user_repo.list_all(conn)
