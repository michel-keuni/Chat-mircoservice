from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
class MessageCreate(BaseModel):
    room_id: str = Field(..., description="Identifiant du salon de discussion")
    user_id: str | None = Field(default=None, description="Identifiant de l'utilisateur")
    content: str = Field(..., min_length=1, max_length=1000, description="Contenu du message")

class MessageResponse(MessageCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., alias="_id", description="Identifiant genere par MongoDb")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Heure d'envoi")
    