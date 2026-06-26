from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user_http
from app.services.call_service import CallService

router = APIRouter(tags=["Calls"])


@router.get("/calls/history/{room_id}")
async def get_call_history(
    room_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user_http)
):
    """
    Récupère l'historique des appels pour un salon de discussion donné.
    """
    # On pourrait ajouter une vérification pour s'assurer que l'utilisateur a accès à ce salon
    history = await CallService.get_call_history(room_id, limit)
    # Conversion des ObjectId en str pour la réponse JSON
    return [{**doc, "_id": str(doc["_id"])} for doc in history]