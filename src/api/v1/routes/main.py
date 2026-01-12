from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from src.api.v1.routes.chat import chat_router
from src.config import settings

api_router = APIRouter(tags=["main"])
api_router.include_router(chat_router)


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
