import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path


class _DBPath:
    _value: str | None = None

    def set(self, path: str):
        self._value = path

    def get(self) -> str:
        if self._value is not None:
            return self._value
        from backend.config import get_settings
        p = Path(get_settings().db_file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p.resolve())


DB_PATH = _DBPath()


async def init_db():
    path = DB_PATH.get()
    schema = Path(__file__).parent.parent.parent / "database" / "schema.sql"
    async with aiosqlite.connect(path) as db:
        await db.executescript(schema.read_text(encoding="utf-8"))
        await db.commit()


@asynccontextmanager
async def get_db():
    path = DB_PATH.get()
    db = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
    finally:
        await db.close()
