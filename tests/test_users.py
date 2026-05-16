def test_create_user_returns_201(client):
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Alice"
    assert "id" in body and len(body["id"]) > 0
    assert "createdAt" in body


def test_create_user_duplicate_name_returns_409(client):
    client.post("/users", json={"name": "Alice"})
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 409
    assert r.json()["error"] == "user_name_taken"


def test_create_user_empty_body_returns_422(client):
    r = client.post("/users", json={})
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_list_users(client):
    client.post("/users", json={"name": "Alice"})
    client.post("/users", json={"name": "Bob"})
    r = client.get("/users")
    assert r.status_code == 200
    names = {u["name"] for u in r.json()}
    assert names == {"Alice", "Bob"}
