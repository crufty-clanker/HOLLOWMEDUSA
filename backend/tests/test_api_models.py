def test_list_models_empty(client):
    resp = client.get("/api/v1/models/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_upsert_model(client, db_session):
    resp = client.put(
        "/api/v1/models/",
        json={
            "id": "test-model",
            "provider": "openai",
            "model_name": "gpt-4o",
            "api_key": "test-key",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "saved"

    # Verify it was saved
    resp = client.get("/api/v1/models/")
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == "test-model"
