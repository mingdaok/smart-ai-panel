# tests/test_expert_repo.py
import pytest
import tempfile
import os
from backend.db.connection import init_db, DB_PATH
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo

_db_path = os.path.join(tempfile.gettempdir(), "test_expert_repo_temp.db")


@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)


@pytest.mark.asyncio
async def test_create_batch():
    DB_PATH.set(_db_path)
    await init_db()
    room_repo = RoomRepo()
    room = await room_repo.create({"topic": "Test", "expert_count": 3})

    repo = ExpertRepo()
    experts_data = [
        {"name": "张教授", "title": "研究员", "stance": "支持", "color": "#6366f1", "role": "host", "position": 0},
        {"name": "李总", "title": "CEO", "stance": "反对", "color": "#3b82f6", "role": "expert", "position": 1},
        {"name": "王工", "title": "工程师", "stance": "中立", "color": "#10b981", "role": "expert", "position": 2},
    ]
    result = await repo.create_batch(room["id"], experts_data)
    assert len(result) == 3
    assert all("id" in e for e in result)
    assert result[0]["role"] == "host"


@pytest.mark.asyncio
async def test_get_by_room():
    DB_PATH.set(_db_path)
    await init_db()
    room_repo = RoomRepo()
    room = await room_repo.create({"topic": "Test", "expert_count": 2})
    repo = ExpertRepo()
    await repo.create_batch(room["id"], [
        {"name": "A", "title": "T", "stance": "S", "color": "#111", "role": "host", "position": 0},
        {"name": "B", "title": "T", "stance": "S", "color": "#222", "role": "expert", "position": 1},
    ])
    experts = await repo.get_by_room(room["id"])
    assert len(experts) == 2


@pytest.mark.asyncio
async def test_update_state():
    DB_PATH.set(_db_path)
    await init_db()
    room_repo = RoomRepo()
    room = await room_repo.create({"topic": "Test", "expert_count": 1})
    repo = ExpertRepo()
    [expert] = await repo.create_batch(room["id"], [
        {"name": "A", "title": "T", "stance": "S", "color": "#111", "role": "expert", "position": 0},
    ])
    await repo.update_state(expert["id"], "speaking", "正在论证...")
    experts = await repo.get_by_room(room["id"])
    assert experts[0]["current_status"] == "speaking"
    assert experts[0]["public_thought"] == "正在论证..."
