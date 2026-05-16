import os
import sqlite3
from typing import Generator

from app.storage.db import connect, init_schema


def _db_path() -> str:
    return os.environ.get("MESSENGER_DB_PATH", "./messenger.db")


_initialized: set[str] = set()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    path = _db_path()
    conn = connect(path)
    if path not in _initialized:
        init_schema(conn)
        _initialized.add(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def reset_initialization_cache() -> None:
    _initialized.clear()
