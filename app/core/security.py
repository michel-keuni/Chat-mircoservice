

from typing import Optional

from fastapi import HTTPException, Security, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import PyJWTError
from app.core.config import setting


security_scheme = HTTPBearer()

def verify_jwt_token(token: str) -> dict:
    # Valide le token et retourne les donnees du user
    try:
        payload = jwt.decode(token,setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        return payload
    except PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials (invalid token)"
        )

async def get_current_user_http(credentials: HTTPAuthorizationCredentials = Security(security_scheme)) -> dict:
    # Dépendance pour sécuriser les routes REST
    return verify_jwt_token(credentials.credentials)

async def get_current_user_ws(websocket: WebSocket, token: Optional[str]):
    # Dépendance pour sécuriser les connexions WebSocket
    if not token: 
        await websocket.close(code=4008, reason="Token missing in query parameters")
        raise HTTPException(status_code=401, detail="Token missing")
    
    return verify_jwt_token(token)
def create_access_token(data: dict) -> str:
    
    return jwt.encode(data,setting.SECRET_KEY, algorithm=setting.ALGORITHM )