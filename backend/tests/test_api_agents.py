def test_list_agents_empty(client):
    resp = client.get("/api/v1/agents/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_agent(client, db_session):
    from hollowmedusa.storage.repositories.agent_repository import AgentRepository

    repo = AgentRepository(db_session)
    repo.create("test-agent", {"system_prompt": "test", "primary_model": "openai/gpt-4o-mini"})

    resp = client.put("/api/v1/agents/test-agent", json={"system_prompt": "updated"})
    assert resp.status_code == 200
    assert resp.json()["config"]["system_prompt"] == "updated"


def test_update_agent_not_found(client):
    resp = client.put("/api/v1/agents/nonexistent", json={"system_prompt": "test"})
    assert resp.status_code == 404
