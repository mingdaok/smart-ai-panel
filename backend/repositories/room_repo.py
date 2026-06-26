import uuid
from datetime import datetime, timezone
from backend.db.connection import get_db


class RoomRepo:
    async def create(self, data: dict) -> dict:
        room_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                "INSERT INTO rooms (id, topic, expert_count, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (room_id, data["topic"], data.get("expert_count", 4), "waiting", now, now)
            )
            await db.commit()
        return await self.get_by_id(room_id)

    async def list_all(self) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM rooms ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_by_id(self, room_id: str) -> dict | None:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_status(self, room_id: str, status: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                "UPDATE rooms SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, room_id)
            )
            await db.commit()
