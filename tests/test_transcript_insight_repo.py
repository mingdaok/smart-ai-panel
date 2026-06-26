# tests/test_transcript_insight_repo.py
import pytest
import tempfile
import os
from backend.db.connection import init_db, DB_PATH
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo

_db_path = os.path.join(tempfile.gettempdir(), "test_transcript_insight_temp.db")


@pytest.fixture(autouse=True)
def cleanup_file():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)


@pytest.mark.asyncio
async def test_add_and_get_transcript():
    DB_PATH.set(_db_path)
    await init_db()
    room = await RoomRepo().create({"topic": "T", "expert_count": 1})
    [expert] = await ExpertRepo().create_batch(room["id"], [
        {"name": "A", "title": "T", "stance": "S", "color": "#111", "role": "expert", "position": 0}
    ])
    repo = TranscriptRepo()
    line = await repo.add({
        "room_id": room["id"], "expert_id": expert["id"], "content": "我认为...",
        "line_type": "argument", "sequence_num": 1
    })
    assert line["content"] == "我认为..."
    assert line["line_type"] == "argument"

    lines = await repo.get_by_room(room["id"])
    assert len(lines) == 1


@pytest.mark.asyncio
async def test_add_and_get_insights():
    DB_PATH.set(_db_path)
    await init_db()
    room = await RoomRepo().create({"topic": "T", "expert_count": 1})
    repo = InsightRepo()
    i1 = await repo.add(room["id"], "consensus", "双方认同需要监管")
    i2 = await repo.add(room["id"], "disagreement", "监管力度存分歧")

    insights = await repo.get_by_room(room["id"])
    assert len(insights) == 2
    assert insights[0]["type"] == "consensus"
    assert insights[1]["type"] == "disagreement"
