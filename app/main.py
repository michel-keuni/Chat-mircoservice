from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import setting
from app.api.v1.router import api_v1_router
# Nous importerons nos futurs routeurs ici plus tard

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Demarrage du micro-service de chat...")

    yield

    print("Arret du mico-service et fermeture des connexions...")

# Metadata pour l'UI OpenAPI/Swagger
tags_metadata = [
    {"name": "Calls", "description": "Endpoints pour l'historique et la gestion des appels"},
    {"name": "Chat  History & REST", "description": "Endpoints REST pour envoyer et récupérer les messages"},
    {"name": "WebSocket Real-Time", "description": "Endpoints WebSocket pour la communication temps réel (JSON)"},
]

app = FastAPI(
    title=setting.PROJECT_NAME,
    version="1.0.0.0",
    description=(
        "Micro-service de chat en temps réel.\n\n"
        "WebSocket: tous les messages reçus par les endpoints WebSocket doivent être envoyés au format JSON. "
        "Le format général attendu est : {\"type\": \"<event_type>\", \"payload\": { ... } }.\n\n"
        "Exemples de `type` et `payload` :\n"
        "- chat_message : payload = {\"content\": \"Bonjour !\"} (le serveur enrichit et rediffuse le message)\n"
        "- call_request / call_ringing / call_accepted / call_rejected / call_ended : payload = { ... signalisation WebRTC ... }\n"
        "- voip_offer / voip_answer / ice_candidate : payload = {\"sdp\": ..., \"candidate\": ... }\n\n"
        "Les endpoints REST exposent l'historique et la persistance (MongoDB). Voir la documentation des routes `/api/v1` pour les schémas REST."
    ),
    contact={
        "name": "Michel Le Roi",
        "url": "https://example.com",
        "email": "michel@example.com",
    },
    license_info={"name": "MIT"},
    terms_of_service="https://example.com/terms",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Les tags OpenAPI sont enregistrés via `openapi_tags` fourni au constructeur

app.include_router(api_v1_router, prefix="/api/v1")  # noqa: F821

@app.get("/health")
async def health_check():
    #Route pour v'erifier si le service tourne correctement
    return {"status": "healthy"}