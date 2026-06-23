

from typing import List

from fastapi import APIRouter, status

from app.schemas.message import MessageCreate, MessageResponse
from app.services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["Chat  History & REST"])

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(message: MessageCreate):
    saved_message = await ChatService.save_message(message)
    return saved_message


@router.get("/history/{room_id}", response_model=List[MessageResponse])
async def get_history(room_id: str, limit: int = 50):

    messages = await ChatService.get_room_history(room_id, limit=limit)
    if not messages:
        return []
    return messages