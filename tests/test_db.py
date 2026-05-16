import sqlite3
from pathlib import Path

import pytest

from app.storage.db import connect, init_schema


def test_init_schema_creates_all_tables(tmp_path: Path):
    db_path = tmp_path / "test.db"
    conn = connect(str(db_path))
    init_schema(conn)

    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = {row[0] for row in cur.fetchall()}

    assert "users" in tables
    assert "conversations" in tables
    assert "conversation_participants" in tables
    assert "messages" in tables
    assert "messages_fts" in tables


def test_foreign_keys_enforced(tmp_path: Path):
    db_path = tmp_path / "test.db"
    conn = connect(str(db_path))
    init_schema(conn)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO messages(id, conversation_id, sender_id, text, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("m1", "nonexistent-conv", "nonexistent-user", "hi", "2026-01-01T00:00:00Z"),
        )


def test_fts_triggers_keep_index_in_sync(tmp_path: Path):
    db_path = tmp_path / "test.db"
    conn = connect(str(db_path))
    init_schema(conn)

    # Seed: a user, conversation, and message (FKs satisfied)
    conn.executescript(
        """
        INSERT INTO users(id, name, created_at) VALUES ('u1', 'Alice', '2026-01-01T00:00:00Z');
        INSERT INTO conversations(id, type, created_at) VALUES ('c1', 'direct', '2026-01-01T00:00:00Z');
        INSERT INTO conversation_participants(conversation_id, user_id) VALUES ('c1', 'u1');
        INSERT INTO messages(id, conversation_id, sender_id, text, created_at)
            VALUES ('m1', 'c1', 'u1', 'the quick brown fox', '2026-01-01T00:00:00Z');
        """
    )
    conn.commit()

    # Insert trigger: text searchable
    rows = conn.execute(
        "SELECT m.id FROM messages_fts f JOIN messages m ON m.rowid = f.rowid "
        "WHERE messages_fts MATCH 'quick'"
    ).fetchall()
    assert [r["id"] for r in rows] == ["m1"]

    # Update trigger: old token gone, new token findable
    conn.execute("UPDATE messages SET text = 'lazy dog jumps' WHERE id = 'm1'")
    conn.commit()
    assert conn.execute(
        "SELECT 1 FROM messages_fts WHERE messages_fts MATCH 'quick'"
    ).fetchone() is None
    assert conn.execute(
        "SELECT 1 FROM messages_fts WHERE messages_fts MATCH 'lazy'"
    ).fetchone() is not None

    # Delete trigger: row removed from FTS index
    conn.execute("DELETE FROM messages WHERE id = 'm1'")
    conn.commit()
    assert conn.execute(
        "SELECT 1 FROM messages_fts WHERE messages_fts MATCH 'lazy'"
    ).fetchone() is None


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
