from datetime import datetime
from bson import ObjectId
from app.core.database import db
from app.schemas.call import CallCreate


class CallService:
    @staticmethod
    async def create_call(call_data: CallCreate) -> str:
        """Crée une nouvelle entrée d'appel dans la base de données avec le statut 'ongoing'."""
        call_doc = {
            "room_id": call_data.room_id,
            "caller_id": call_data.caller_id,
            "start_time": datetime.utcnow(),
            "status": "ongoing"
        }
        result = await db.calls.insert_one(call_doc)
        return str(result.inserted_id)

    @staticmethod
    async def end_call(call_id: str, status: str):
        """Met à jour un appel pour marquer sa fin et calculer sa durée."""
        end_time = datetime.utcnow()
        call_oid = ObjectId(call_id)

        call = await db.calls.find_one({"_id": call_oid})
        if not call or "start_time" not in call:
            return

        duration = (end_time - call["start_time"]).total_seconds()

        await db.calls.update_one(
            {"_id": call_oid},
            {"$set": {"end_time": end_time, "status": status, "duration": int(duration)}}
        )

    @staticmethod
    async def get_call_history(room_id: str, limit: int = 50) -> list[dict]:
        """Récupère l'historique des appels pour un salon donné."""
        cursor = db.calls.find({"room_id": room_id}).sort("start_time", -1).limit(limit)
        return [doc async for doc in cursor]