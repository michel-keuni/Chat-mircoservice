
import json
import asyncio
from app.core.security import get_current_user_ws
from app.services.chat_service import ChatService
from app.services.redis_service import RedisService, redis_client
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager
from app.schemas.message import MessageCreate

router = APIRouter(tags=["WebSocket Real-Time"])

async def pub_listener(websocket: WebSocket, room_id: str | None, user_id: str | None = None):
    """
        Tache en arriere plan qui ecoute les evenemets publi'es sur le canal
        Redis et les pousses immediatement sur le websocket de l'utilisateur
    """

    if not room_id and not user_id:
        return
    
    channel = f"room:{room_id}" if room_id else f"user:{user_id}"

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

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


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket:WebSocket, room_id: str, token: str | None = None):
    """
    Point d'entrée WebSocket. Gère la connexion, l'enregistrement, 
    la réception de messages et lance l'écoute de Redis.
    """

    user_payload = await get_current_user_ws(websocket, token)
    authenticated_user_id = user_payload.get("sub")

    if not authenticated_user_id:
        await websocket.close(code=4008, reason="Invalid token payload")
        return

    await manager.connect(websocket, room_id)

    # Lancement de la tache d'ecoute Redis en arriere plan pour le client
    listener_task = asyncio.create_task(pub_listener(websocket, room_id, None))

    try:
        while True:
            data = await websocket.receive_text()
            content = data.strip()

            if content:
                message_create = MessageCreate(
                    room_id=room_id,
                    user_id=authenticated_user_id,
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


@router.websocket("/ws/user/")
async def websocket_endpoint_user(websocket:WebSocket, token: str | None = None):
    """
    Point d'entrée WebSocket pour une connexion utilisateur globale.
    Permet à l'utilisateur de recevoir des notifications (par exemple, pour de nouveaux DM)
    lorsqu'il n'est pas dans un salon de discussion spécifique.
    Cette connexion est principalement en écoute seule.
    """
    user_payload = await get_current_user_ws(websocket, token)
    authenticated_user_id = user_payload.get("sub")

    if not authenticated_user_id:
        await websocket.close(code=4008, reason="Invalid token payload")
        return

    await manager.connect(websocket, authenticated_user_id)
    # Lance l'écoute sur le canal Redis personnel de l'utilisateur
    listener_task = asyncio.create_task(pub_listener(websocket, None, authenticated_user_id))
    try:
        while True:
            # Maintient la connexion ouverte pour écouter les messages de Redis.
            # Le client n'est pas censé envoyer de messages sur ce canal.
            # On peut ajouter un 'ping' périodique si nécessaire pour maintenir la connexion.
            await websocket.receive_text() # Attend passivement

    except WebSocketDisconnect:
        # Le client s'est déconnecté, on nettoie.
        manager.disconnect(websocket, authenticated_user_id)
        listener_task.cancel()
    except Exception as e:
        print(f"Erreur inattendue sur le websocket utilisateur: {e}")
        manager.disconnect(websocket, authenticated_user_id)
        listener_task.cancel()