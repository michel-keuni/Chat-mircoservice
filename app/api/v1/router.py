
from fastapi import APIRouter

from app.api.v1.endpoints import call, chat, websocket


api_v1_router = APIRouter()
api_v1_router.include_router(chat.router)
api_v1_router.include_router(call.router)
api_v1_router.include_router(websocket.router)