
import json
import asyncio
from app.services.chat_service import ChatService
from app.services.redis_service import RedisService, redis_client
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager
from app.schemas.message import MessageCreate
router = APIRouter(tags=["WebSocket Real-Time"])

async def pub_listener(websocket: WebSocket, room_id: str):
    """
        Tache en arriere plan qui ecoute les evenemets publi'es sur le canal
        Redis et les pousses immediatement sur le websocket de l'utilisateur
    """

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"room:{room_id}")

    try:
        while True:
            # On attend un message du canal Redis avec un timeout l'eger
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                payload = json.loads(message["data"])
                await websocket.send_json(payload)
            await asyncio.sleep(0.01) #Evite de saturer le CPU
    
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.close()


@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket:WebSocket, room_id: str, user_id: str):
    """
    Point d'entrée WebSocket. Gère la connexion, l'enregistrement, 
    la réception de messages et lance l'écoute de Redis.
    """

    await manager.connect(websocket, room_id)

    # Lancement de la tache d'ecoute Redis en arriere plan pour le client
    listener_task = asyncio.create_task(pub_listener(websocket, room_id))

    try:
        while True:
            data = await websocket.receive_text()
            content = data.strip()

            if content:
                message_create = MessageCreate(
                    room_id=room_id,
                    user_id=user_id,
                    content=content
                )

                # Sauvegarde dans MongoDB
                saved_message = await ChatService.save_message(message_create)

                # Publication du message sur Redis (Pour diffusion temps reelle)
                saved_message["timestamp"] = saved_message["timestamp"].isoformat()
                await RedisService.publish_message(room_id, saved_message)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        listener_task.cancel()
    except Exception as e:
        print(f"Erreur innatendue sur le websocket: {e}")
        manager.disconnect(websocket, room_id)
        listener_task.cancel()