import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token
from app.core.database import db

# Fixture du client partagée pour TOUTE la session de test
@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

# Fixture pour générer le token (générée à chaque fonction si nécessaire)
@pytest.fixture(scope="function")
def auth_headers():
    token = create_access_token({"sub": "tester_99"})
    print(f"\n--------TOKEN DE TEST {token}")
    return {"Authorization": f"Bearer {token}"}

# Nettoyage automatique exécuté APRÈS chaque test unique
@pytest.fixture(autouse=True, scope="function")
async def clean_database():
    yield
    # S'exécute sagement après chaque test sur la boucle unique toujours active
    await db.messages.delete_many({})
    await db.calls.delete_many({})