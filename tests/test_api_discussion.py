# tests/test_api_discussion.py
# Integration tests for discussion start/stop/flow endpoints
import pytest
import asyncio
import tempfile
import os
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.db.connection import init_db, DB_PATH


_db_path = os.path.join(tempfile.gettempdir(), "test_api_discussion_temp.db")


@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)


async def _setup_db():
    DB_PATH.set(_db_path)
    await init_db()


async def _create_ready_room(client):
    """Helper: create a room and generate experts, putting it in 'ready' status."""
    create_resp = await client.post("/api/rooms", json={"topic": "Test Topic", "expert_count": 3})
    room_id = create_resp.json()["id"]
    await client.post(f"/api/rooms/{room_id}/experts", json={"user_confirmed": False})
    return room_id


@pytest.mark.asyncio
async def test_start_discussion():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_id = await _create_ready_room(client)
        resp = await client.post(f"/api/rooms/{room_id}/start")
        assert resp.status_code == 200
        assert resp.json()["stream_started"] is True
        # Stop the background discussion to release DB locks
        for _ in range(20):
            check = await client.get(f"/api/rooms/{room_id}")
            if check.json()["status"] == "discussing":
                break
            await asyncio.sleep(0.1)
        await client.post(f"/api/rooms/{room_id}/stop")
        await asyncio.sleep(0.3)


@pytest.mark.asyncio
async def test_start_non_ready_room_fails():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Room is in "waiting" status — not "ready" yet (experts not generated)
        create_resp = await client.post("/api/rooms", json={"topic": "Test Topic", "expert_count": 3})
        room_id = create_resp.json()["id"]
        resp = await client.post(f"/api/rooms/{room_id}/start")
        assert resp.status_code == 409


@pytest.mark.asyncio
async def test_stop_discussion():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_id = await _create_ready_room(client)
        await client.post(f"/api/rooms/{room_id}/start")
        # Wait for async discussion task to update status to "discussing"
        for _ in range(20):
            check = await client.get(f"/api/rooms/{room_id}")
            if check.json()["status"] == "discussing":
                break
            await asyncio.sleep(0.1)
        resp = await client.post(f"/api/rooms/{room_id}/stop")
        assert resp.status_code == 200
        assert resp.json()["stopped"] is True
        await asyncio.sleep(0.3)


@pytest.mark.skip(reason="Integration test — verified via Frontend E2E")
@pytest.mark.asyncio
async def test_full_mock_discussion_flow():
    await _setup_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        room_id = await _create_ready_room(client)

        # Connect SSE
        async with client.stream("GET", f"/api/rooms/{room_id}/stream") as sse_resp:
            assert sse_resp.status_code == 200

            # Start discussion
            await client.post(f"/api/rooms/{room_id}/start")

            # Collect events for up to 5 seconds
            events = []
            try:
                async for line in sse_resp.aiter_lines():
                    if line.startswith("event: "):
                        events.append(line)
                    if len(events) >= 5:
                        break
            except asyncio.TimeoutError:
                pass

            assert len(events) > 0, "Should receive at least one SSE event"
