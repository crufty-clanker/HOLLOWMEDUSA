def test_create_run(client):
    resp = client.post("/api/v1/runs/", json={"graph_id": "default"})
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["status"] == "running"


def test_get_run_not_found(client):
    resp = client.get("/api/v1/runs/nonexistent")
    assert resp.status_code == 404


def test_get_run_trace(client, db_session):
    resp = client.post("/api/v1/runs/", json={})
    run_id = resp.json()["id"]
    resp = client.get(f"/api/v1/runs/{run_id}/trace")
    assert resp.status_code == 200
    assert "step_results" in resp.json()


def test_retry_step(client, db_session):
    resp = client.post("/api/v1/runs/", json={})
    run_id = resp.json()["id"]
    resp = client.post(f"/api/v1/runs/{run_id}/step/test_step/retry")
    assert resp.status_code == 200
    assert resp.json()["status"] == "retry initiated"
