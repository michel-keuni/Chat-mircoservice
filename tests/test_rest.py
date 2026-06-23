import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response= await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_create_and_get_message():
    room_id="test_room_123"
    user_id="tester_99"
    content="Hello, this is an automated unit test."

    # Envoi du message
    payload = {
        "room_id":room_id,
        "user_id": user_id,
        "content": content
    }

    async with  AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/api/v1/chat/messages", json=payload)

    assert create_response.status_code==201
    data = create_response.json()
    assert data["room_id"] == room_id
    assert data["user_id"] == user_id
    assert data["content"] == content
    assert "_id" in data

    #Recuperation de l'historique
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        history_response = await ac.get(f"/api/v1/chat/history/{room_id}")
    
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert isinstance(history_data, list)
    assert len(history_data) > 0
    assert history_data[-1]["content"] == content

