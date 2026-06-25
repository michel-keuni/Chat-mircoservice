
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_key: str):
        # Accepte la connexion WebSocket et l'enregistre sous une clé de groupe (room_id ou user_id)
        await websocket.accept()
        if group_key not in self.active_connections:
            self.active_connections[group_key] = []
        self.active_connections[group_key].append(websocket)

    def disconnect(self, websocket: WebSocket, group_key: str):
        # Retire la connexion WebSocket du groupe
        if group_key in self.active_connections:
            self.active_connections[group_key].remove(websocket)
            if not self.active_connections[group_key]:
                del self.active_connections[group_key]
        
    async def broadcast_to_group(self, message: dict, group_key: str):
        # Diffuse un message JSON à tous les utilisateurs connectés à un groupe
        if group_key in self.active_connections:
            for connection in self.active_connections[group_key]:
                await connection.send_json(message)


manager = ConnectionManager()
