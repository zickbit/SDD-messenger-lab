def _setup_with_messages(client, texts: list[str]) -> tuple[str, str, str]:
    a = client.post("/users", json={"name": "Alice"}).json()["id"]
    b = client.post("/users", json={"name": "Bob"}).json()["id"]
    conv = client.post("/conversations",
                       json={"participantIds": [a, b]}).json()["id"]
    for t in texts:
        client.post("/messages",
                    json={"conversationId": conv, "senderId": a, "text": t})
    return a, b, conv


def test_search_basic_match(client):
    _setup_with_messages(client, ["Hello world", "Goodbye", "Hello there"])
    r = client.get("/messages/search?q=hello")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    texts = {m["text"] for m in body["results"]}
    assert texts == {"Hello world", "Hello there"}


def test_search_filter_by_conversation(client):
    a = client.post("/users", json={"name": "Alice"}).json()["id"]
    b = client.post("/users", json={"name": "Bob"}).json()["id"]
    c = client.post("/users", json={"name": "Carol"}).json()["id"]
    conv1 = client.post("/conversations",
                        json={"participantIds": [a, b]}).json()["id"]
    conv2 = client.post("/conversations",
                        json={"participantIds": [a, c]}).json()["id"]
    client.post("/messages",
                json={"conversationId": conv1, "senderId": a, "text": "hello in 1"})
    client.post("/messages",
                json={"conversationId": conv2, "senderId": a, "text": "hello in 2"})

    r = client.get(f"/messages/search?q=hello&conversationId={conv1}")
    body = r.json()
    assert body["total"] == 1
    assert body["results"][0]["text"] == "hello in 1"


def test_search_filter_by_sender(client):
    a = client.post("/users", json={"name": "Alice"}).json()["id"]
    b = client.post("/users", json={"name": "Bob"}).json()["id"]
    conv = client.post("/conversations",
                       json={"participantIds": [a, b]}).json()["id"]
    client.post("/messages",
                json={"conversationId": conv, "senderId": a, "text": "from alice"})
    client.post("/messages",
                json={"conversationId": conv, "senderId": b, "text": "from bob"})

    r = client.get(f"/messages/search?q=from&senderId={a}")
    body = r.json()
    assert body["total"] == 1
    assert body["results"][0]["text"] == "from alice"


def test_search_pagination(client):
    _setup_with_messages(client, [f"keyword msg-{i}" for i in range(5)])
    r = client.get("/messages/search?q=keyword&limit=2&offset=0")
    body = r.json()
    assert body["total"] == 5
    assert len(body["results"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 0

    r2 = client.get("/messages/search?q=keyword&limit=2&offset=2")
    assert len(r2.json()["results"]) == 2


def test_search_short_query_returns_400(client):
    r = client.get("/messages/search?q=a")
    assert r.status_code == 400
    assert r.json()["error"] == "invalid_search_query"


def test_search_empty_query_returns_422(client):
    r = client.get("/messages/search")
    assert r.status_code == 422


def test_search_special_characters_do_not_crash(client):
    _setup_with_messages(client, ["hello world"])
    r = client.get('/messages/search?q="OR%20*')
    assert r.status_code == 200
