def _setup(client):
    a = client.post("/users", json={"name": "Alice"}).json()["id"]
    b = client.post("/users", json={"name": "Bob"}).json()["id"]
    conv = client.post("/conversations",
                       json={"participantIds": [a, b]}).json()["id"]
    return a, b, conv


def test_send_message_returns_201(client):
    a, _, conv = _setup(client)
    r = client.post("/messages", json={
        "conversationId": conv, "senderId": a, "text": "Hello",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["text"] == "Hello"
    assert body["senderId"] == a
    assert body["conversationId"] == conv


def test_send_message_empty_text_returns_400(client):
    a, _, conv = _setup(client)
    r = client.post("/messages",
                    json={"conversationId": conv, "senderId": a, "text": "  "})
    assert r.status_code == 400
    assert r.json()["error"] == "empty_message"


def test_send_message_unknown_sender_returns_404(client):
    _, _, conv = _setup(client)
    r = client.post("/messages",
                    json={"conversationId": conv, "senderId": "ghost", "text": "hi"})
    assert r.status_code == 404
    assert r.json()["error"] == "user_not_found"


def test_send_message_unknown_conversation_returns_404(client):
    a, _, _ = _setup(client)
    r = client.post("/messages",
                    json={"conversationId": "ghost", "senderId": a, "text": "hi"})
    assert r.status_code == 404
    assert r.json()["error"] == "conversation_not_found"


def test_send_message_non_participant_returns_403(client):
    a, _, conv = _setup(client)
    outsider = client.post("/users", json={"name": "Eve"}).json()["id"]
    r = client.post("/messages",
                    json={"conversationId": conv, "senderId": outsider, "text": "hi"})
    assert r.status_code == 403
    assert r.json()["error"] == "not_a_participant"


def test_history_returns_messages_newest_first(client):
    a, _, conv = _setup(client)
    for i in range(3):
        client.post("/messages",
                    json={"conversationId": conv, "senderId": a, "text": f"msg-{i}"})
    r = client.get(f"/conversations/{conv}/messages")
    assert r.status_code == 200
    msgs = r.json()["messages"]
    assert [m["text"] for m in msgs] == ["msg-2", "msg-1", "msg-0"]


def test_history_pagination(client):
    a, _, conv = _setup(client)
    for i in range(7):
        client.post("/messages",
                    json={"conversationId": conv, "senderId": a, "text": f"msg-{i}"})

    page1 = client.get(f"/conversations/{conv}/messages?limit=3").json()
    assert len(page1["messages"]) == 3
    assert [m["text"] for m in page1["messages"]] == ["msg-6", "msg-5", "msg-4"]
    assert page1["nextBefore"] is not None

    page2 = client.get(
        f"/conversations/{conv}/messages?limit=3&before={page1['nextBefore']}"
    ).json()
    assert [m["text"] for m in page2["messages"]] == ["msg-3", "msg-2", "msg-1"]
    assert page2["nextBefore"] is not None

    page3 = client.get(
        f"/conversations/{conv}/messages?limit=3&before={page2['nextBefore']}"
    ).json()
    assert [m["text"] for m in page3["messages"]] == ["msg-0"]
    assert page3["nextBefore"] is None


def test_history_unknown_conversation_returns_404(client):
    r = client.get("/conversations/ghost/messages")
    assert r.status_code == 404
    assert r.json()["error"] == "conversation_not_found"
