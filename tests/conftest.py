import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("MESSENGER_DB_PATH", str(db_path))

    from app.api import deps
    deps.reset_initialization_cache()

    from app.api.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c
