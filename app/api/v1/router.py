
from fastapi import APIRouter

from app.api.v1.endpoints import chat, websocket


api_v1_router = APIRouter()
api_v1_router.include_router(chat.router)
api_v1_router.include_router(websocket.router)