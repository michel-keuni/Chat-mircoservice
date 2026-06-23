from pydantic import BaseModel, Field
from datetime import datetime
class MessageCreate(BaseModel):
    room_id: str = Field(..., description="Identifiant du salon de discussion")
    user_id: str = Field(..., description="Identifiant de l'utilisateur")
    content: str = Field(..., min_length=1, max_length=1000, description="Contenu du message")

class MessageResponse(MessageCreate):
    id: str = Field(..., alias="_id", description="Identifiant genere par MongoDb")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Heure d'envoi")
    class Config:
        populate_by_name = True