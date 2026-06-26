import pytest
import tempfile
import os
from backend.db.connection import get_db, init_db, DB_PATH

_db_path = os.path.join(tempfile.gettempdir(), "test_ai_panel_temp.db")


@pytest.mark.asyncio
async def test_init_db_creates_tables():
    DB_PATH.set(_db_path)  # use temp file for test
    await init_db()
    async with get_db() as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] async for row in cursor]
        assert "rooms" in tables
        assert "experts" in tables
        assert "transcript_lines" in tables
        assert "insights" in tables
        assert "discussion_events" in tables


@pytest.mark.asyncio
async def test_get_db_returns_connection():
    DB_PATH.set(_db_path)
    await init_db()
    async with get_db() as db:
        cursor = await db.execute("SELECT 1")
        row = await cursor.fetchone()
        assert row[0] == 1


@pytest.fixture(autouse=True)
def cleanup_db():
    yield
    if os.path.exists(_db_path):
        os.remove(_db_path)
