import pytest
from app.core.database import db

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_and_get_message(async_client, auth_headers):
    room_id = "test_room_123"
    content = "Hello, this is an automated unit test."

    payload = {
        "room_id": room_id,
        "content": content
    }

    # Utilisation du client injecté via la fixture
    create_response = await async_client.post("/api/v1/chat/messages", json=payload, headers=auth_headers)

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["room_id"] == room_id
    assert data["user_id"] == "tester_99"
    assert data["content"] == content
    assert "_id" in data

    # Récupération de l'historique
    history_response = await async_client.get(f"/api/v1/chat/history/{room_id}")
    
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert isinstance(history_data, list)
    assert len(history_data) > 0
    assert history_data[-1]["content"] == content