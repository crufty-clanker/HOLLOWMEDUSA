def test_list_contexts_empty(client):
    resp = client.get("/api/v1/contexts/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_context(client, db_session):
    resp = client.post(
        "/api/v1/contexts/",
        json={
            "id": "test-context",
            "name": "Test Context",
            "description": "A test context",
            "files": ["test.md"],
            "steps": ["requirements"],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Context"


def test_update_context(client, db_session):
    # Create first
    client.post(
        "/api/v1/contexts/",
        json={"id": "test-ctx", "name": "Original", "files": [], "steps": []},
    )

    # Update
    resp = client.put(
        "/api/v1/contexts/test-ctx",
        json={"id": "test-ctx", "name": "Updated", "files": ["new.md"], "steps": ["code"]},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"
