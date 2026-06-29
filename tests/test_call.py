import pytest
from app.core.security import create_access_token
from app.core.database import db

@pytest.mark.asyncio
async def test_get_call_history(async_client):
    user_id = "testuser_calls"
    room_id = "testuser_calls_anotheruser"
    token = create_access_token(data={"sub": user_id})

    await db.calls.delete_many({"room_id": room_id})

    await db.calls.insert_one({
        "room_id": room_id,
        "caller_id": user_id,
        "status": "completed",
        "duration": 60
    })

    # Utilisation du client asynchrone centralisé
    response = await async_client.get(
        f"/api/v1/calls/history/{room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["room_id"] == room_id
    assert data[0]["status"] == "completed"