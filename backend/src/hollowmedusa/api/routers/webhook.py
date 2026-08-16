"""Webhook handler for CI/CD triggers."""
from fastapi import APIRouter, Request, HTTPException
from typing import Any

router = APIRouter()


@router.post("/github")
async def github_webhook(request: Request) -> dict[str, Any]:
    """Handle GitHub push events to trigger pipeline."""
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "")

    if event != "push":
        raise HTTPException(status_code=400, detail="Unsupported event")

    # TODO: Extract branch, trigger pipeline
    return {"status": "received", "event": event, "ref": payload.get("ref")}
