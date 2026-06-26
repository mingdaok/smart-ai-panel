import uuid
from datetime import datetime, timezone
from backend.db.connection import get_db


class InsightRepo:
    async def add(self, room_id: str, type_: str, content: str) -> dict:
        insight_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                "INSERT INTO insights (id, room_id, type, content, version, updated_at) VALUES (?,?,?,?,1,?)",
                (insight_id, room_id, type_, content, now)
            )
            await db.commit()
        return {"id": insight_id, "room_id": room_id, "type": type_, "content": content, "version": 1, "updated_at": now}

    async def get_by_room(self, room_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM insights WHERE room_id = ? ORDER BY updated_at", (room_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
