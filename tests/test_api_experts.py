import pytest
import tempfile
import os
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH

_db_path = os.path.join(tempfile.gettempdir(), "test_api_experts_temp.db")


@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)


async def _setup_db():
    DB_PATH.set(_db_path)
    await init_db()


@pytest.mark.asyncio
async def test_generate_experts():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "AI 监管", "expert_count": 4})
        room_id = create_resp.json()["id"]

        resp = await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
        assert resp.status_code == 200
        data = resp.json()
        assert "host" in data
        assert "experts" in data
        assert len(data["experts"]) == 4
        assert data["host"]["role"] == "host"


@pytest.mark.asyncio
async def test_regenerate_returns_409():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post("/api/rooms", json={"topic": "Test", "expert_count": 3})
        room_id = create_resp.json()["id"]
        await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
        resp = await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
        assert resp.status_code == 409


@pytest.mark.asyncio
async def test_experts_nonexistent_room():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/rooms/nonexistent/experts", json={"user_confirmed": False})
        assert resp.status_code == 404
