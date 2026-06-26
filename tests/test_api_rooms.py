import pytest
import tempfile
import os
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH

_db_path = os.path.join(tempfile.gettempdir(), "test_api_rooms_temp.db")


@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)


async def _setup_db():
    DB_PATH.set(_db_path)
    await init_db()


@pytest.mark.asyncio
async def test_create_room():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/rooms", json={"topic": "AI 监管", "expert_count": 4})
        assert resp.status_code == 201
        data = resp.json()
        assert data["topic"] == "AI 监管"
        assert data["status"] == "waiting"
        assert "id" in data


@pytest.mark.asyncio
async def test_create_room_validation():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/rooms", json={"topic": "", "expert_count": 1})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_rooms():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/rooms", json={"topic": "Room A", "expert_count": 3})
        await client.post("/api/rooms", json={"topic": "Room B", "expert_count": 5})
        resp = await client.get("/api/rooms")
        assert resp.status_code == 200
        data = resp.json()
        assert "rooms" in data
        assert len(data["rooms"]) == 2


@pytest.mark.asyncio
async def test_get_room_detail():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 4})
        room_id = create_resp.json()["id"]
        resp = await client.get(f"/api/rooms/{room_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == room_id


@pytest.mark.asyncio
async def test_get_room_404():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/rooms/nonexistent-id")
        assert resp.status_code == 404
