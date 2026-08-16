def test_get_graph_empty(client):
    resp = client.get("/api/v1/graph/")
    assert resp.status_code == 200
    assert resp.json()["topology"] == {}


def test_update_graph(client, db_session):
    topology = {
        "nodes": [{"id": "1", "data": {"label": "Test"}}],
        "edges": [],
    }
    resp = client.put("/api/v1/graph/", json={"topology": topology})
    assert resp.status_code == 200
    assert resp.json()["status"] == "saved"

    # Verify it was saved
    resp = client.get("/api/v1/graph/")
    assert resp.json()["topology"]["nodes"][0]["id"] == "1"
