import redis.asyncio as aioredis
from app.core.config import setting

# Initialisation du client Redis asynchrone
redis_client = aioredis.from_url(
    setting.REDIS_URL,
    decode_responses=True
)

class RedisService:
    @staticmethod
    async def publish_message(room_id: str, message: dict, receiver_id: str | None = None):
        """
        Publie un message sur le canal Redis du salon (room).
        Si un receiver_id est fourni (cas d'un DM), publie également une notification
        sur le canal personnel de ce destinataire.
        """
        import json
        message_str = json.dumps(message)

        # 1. Publier sur le canal du salon pour les participants actifs
        room_channel = f"room:{room_id}"
        await redis_client.publish(room_channel, message_str)

        # 2. Si c'est un DM, publier aussi sur le canal de l'utilisateur destinataire
        #    pour qu'il reçoive une notification s'il n'est pas dans le salon.
        if receiver_id:
            user_channel = f"user:{receiver_id}"
            await redis_client.publish(user_channel, message_str)
