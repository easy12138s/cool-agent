from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from src.config import settings

api_router = APIRouter(tags=["main"])


class EchoRequest(BaseModel):
    message: str


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@api_router.get("/meta")
def meta() -> dict[str, str]:
    return {
        "project_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@api_router.post("/echo")
def echo(payload: EchoRequest) -> dict[str, str]:
    return {"message": payload.message}


@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        return
