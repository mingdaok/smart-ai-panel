import uuid
from datetime import datetime, timezone
from backend.db.connection import get_db


class TranscriptRepo:
    async def add(self, data: dict) -> dict:
        line_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with get_db() as db:
            await db.execute(
                """INSERT INTO transcript_lines (id, room_id, expert_id, content, line_type, sequence_num, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (line_id, data["room_id"], data["expert_id"], data["content"],
                 data["line_type"], data["sequence_num"], now)
            )
            await db.commit()
        return {**data, "id": line_id, "created_at": now}

    async def get_by_room(self, room_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                """SELECT t.*, e.name, e.title, e.color FROM transcript_lines t
                   JOIN experts e ON t.expert_id = e.id
                   WHERE t.room_id = ? ORDER BY t.sequence_num""",
                (room_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
