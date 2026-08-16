import pytest
from fastapi.testclient import TestClient
from hollowmedusa.api.main import app


@pytest.mark.asyncio
async def test_websocket_ping_pong():
    with TestClient(app) as client:
        with client.websocket_connect("/runs/test-id/events") as ws:
            ws.send_text("ping")
            data = ws.receive_text()
            assert data == "pong"


@pytest.mark.asyncio
async def test_websocket_disconnect():
    with TestClient(app) as client:
        ws = client.websocket_connect("/runs/test-id/events")
        ws.__enter__()
        ws.__exit__(None, None, None)
        # Should not raise
