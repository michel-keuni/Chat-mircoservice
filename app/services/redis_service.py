import redis.asyncio as aioredis
from app.core.config import setting

# Initialisation du client Redis asynchrone
redis_client = aioredis.from_url(
    setting.REDIS_URL,
    decode_responses=True
)

class RedisService:
    @staticmethod
    async def publish_message(room_id:str, message:dict):
        
        import json
        channel = f"room:{room_id}"
        message_str = json.dumps(message)
        await redis_client.publish(channel, message_str)
