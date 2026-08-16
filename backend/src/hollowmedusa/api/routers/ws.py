import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# In-memory connection store (replace with Redis in production)
connections: dict[str, list[WebSocket]] = {}


@router.websocket("/runs/{run_id}/events")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    connections.setdefault(run_id, []).append(websocket)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if run_id in connections:
            connections[run_id].remove(websocket)
            if not connections[run_id]:
                del connections[run_id]


async def send_event(run_id: str, event: dict):
    """Send event to all connected clients for a run."""
    for ws in connections.get(run_id, []):
        await ws.send_text(json.dumps(event))
