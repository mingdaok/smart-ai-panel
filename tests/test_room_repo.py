import pytest
import tempfile
import os
import uuid
from backend.db.connection import init_db, DB_PATH, get_db
from backend.repositories.room_repo import RoomRepo

_db_path = os.path.join(tempfile.gettempdir(), "test_room_repo_temp.db")


@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)


@pytest.mark.asyncio
async def test_create_room():
    DB_PATH.set(_db_path)
    await init_db()
    repo = RoomRepo()
    room_data = {"topic": "AI 监管", "expert_count": 4}
    result = await repo.create(room_data)
    assert result["topic"] == "AI 监管"
    assert result["expert_count"] == 4
    assert result["status"] == "waiting"
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_list_rooms():
    DB_PATH.set(_db_path)
    await init_db()
    repo = RoomRepo()
    await repo.create({"topic": "Topic A", "expert_count": 3})
    await repo.create({"topic": "Topic B", "expert_count": 5})
    rooms = await repo.list_all()
    assert len(rooms) == 2


@pytest.mark.asyncio
async def test_get_room_by_id():
    DB_PATH.set(_db_path)
    await init_db()
    repo = RoomRepo()
    created = await repo.create({"topic": "Test", "expert_count": 4})
    fetched = await repo.get_by_id(created["id"])
    assert fetched is not None
    assert fetched["topic"] == "Test"


@pytest.mark.asyncio
async def test_get_nonexistent_room():
    DB_PATH.set(_db_path)
    await init_db()
    repo = RoomRepo()
    result = await repo.get_by_id(str(uuid.uuid4()))
    assert result is None


@pytest.mark.asyncio
async def test_update_status():
    DB_PATH.set(_db_path)
    await init_db()
    repo = RoomRepo()
    created = await repo.create({"topic": "Test", "expert_count": 4})
    await repo.update_status(created["id"], "discussing")
    fetched = await repo.get_by_id(created["id"])
    assert fetched["status"] == "discussing"
