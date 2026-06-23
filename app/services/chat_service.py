
from app.schemas.message import MessageCreate
from datetime import datetime
from app.core.database import db
class ChatService:
    @staticmethod
    async def save_message(message_data: MessageCreate) -> dict:
        # Enregistre un message dans la collection mongoDB 'messages'

        message_dict = message_data.model_dump()
        message_dict["timestamp"] = datetime.utcnow()

        # Insertion dans la collection ' messages' 
        result = await db.messages.insert_one(message_dict)
        message_dict["_id"] = str(result.inserted_id)

        return message_dict

    @staticmethod
    async def get_room_history(room_id: str, limit: int = 50)->list:
        
        cursor = db.messages.find({"room_id":room_id}).sort("timestamp", 1).limit(limit)
        messages = []
        async for message in cursor:
            message["_id"] = str(message["_id"])
            messages.append(message)
        
        return messages