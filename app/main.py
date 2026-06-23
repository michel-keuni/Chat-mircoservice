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

app = FastAPI(
    title=setting.PROJECT_NAME,
    version="1.0.0.0",
    lifespan=lifespan
)

app.include_router(api_v1_router, prefix="/api/v1")  # noqa: F821

@app.get("/health")
async def health_check():
    #Route pour v'erifier si le service tourne correctement
    return {"status": "healthy"}