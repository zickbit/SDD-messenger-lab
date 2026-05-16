def _make_users(client) -> tuple[str, str]:
    a = client.post("/users", json={"name": "Alice"}).json()["id"]
    b = client.post("/users", json={"name": "Bob"}).json()["id"]
    return a, b


def test_create_direct_conversation(client):
    a, b = _make_users(client)
    r = client.post("/conversations", json={"participantIds": [a, b]})
    assert r.status_code == 201
    body = r.json()
    assert body["type"] == "direct"
    assert set(body["participantIds"]) == {a, b}
    assert "id" in body


def test_conversation_requires_two_participants(client):
    a, _ = _make_users(client)
    r = client.post("/conversations", json={"participantIds": [a]})
    assert r.status_code == 400
    assert r.json()["error"] == "invalid_participants"


def test_conversation_rejects_duplicate_participants(client):
    a, _ = _make_users(client)
    r = client.post("/conversations", json={"participantIds": [a, a]})
    assert r.status_code == 400
    assert r.json()["error"] == "invalid_participants"


def test_conversation_rejects_unknown_user(client):
    a, _ = _make_users(client)
    r = client.post("/conversations",
                    json={"participantIds": [a, "unknown-id"]})
    assert r.status_code == 404
    assert r.json()["error"] == "user_not_found"


def test_conversation_duplicate_returns_409_with_existing_id(client):
    a, b = _make_users(client)
    first = client.post("/conversations", json={"participantIds": [a, b]}).json()
    r = client.post("/conversations", json={"participantIds": [b, a]})  # reversed
    assert r.status_code == 409
    body = r.json()
    assert body["error"] == "direct_conversation_exists"
    assert body["existingId"] == first["id"]
