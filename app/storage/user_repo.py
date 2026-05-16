import sqlite3
from datetime import datetime, timezone

from app.models.domain import User


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        name=row["name"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def insert(conn: sqlite3.Connection, user: User) -> None:
    conn.execute(
        "INSERT INTO users(id, name, created_at) VALUES (?, ?, ?)",
        (user.id, user.name, user.created_at.isoformat()),
    )


def find_by_name(conn: sqlite3.Connection, name: str) -> User | None:
    row = conn.execute(
        "SELECT id, name, created_at FROM users WHERE name = ?", (name,)
    ).fetchone()
    return _row_to_user(row) if row else None


def exists(conn: sqlite3.Connection, user_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
    return row is not None


def list_all(conn: sqlite3.Connection) -> list[User]:
    rows = conn.execute(
        "SELECT id, name, created_at FROM users ORDER BY created_at"
    ).fetchall()
    return [_row_to_user(r) for r in rows]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
