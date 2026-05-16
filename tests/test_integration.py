def test_full_message_flow(client):
    # 1. Create user Alice
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 201
    alice = r.json()

    # 2. Create user Bob
    r = client.post("/users", json={"name": "Bob"})
    assert r.status_code == 201
    bob = r.json()

    # 3. Create a direct conversation
    r = client.post("/conversations",
                    json={"participantIds": [alice["id"], bob["id"]]})
    assert r.status_code == 201
    conv = r.json()

    # 4. Send a message from Alice to Bob
    r = client.post("/messages", json={
        "conversationId": conv["id"],
        "senderId": alice["id"],
        "text": "Hello Bob",
    })
    assert r.status_code == 201
    msg = r.json()

    # 5. Retrieve conversation history
    r = client.get(f"/conversations/{conv['id']}/messages")
    assert r.status_code == 200
    history = r.json()

    # 6. Verify the message is present
    assert any(
        m["id"] == msg["id"] and m["text"] == "Hello Bob"
        for m in history["messages"]
    )
