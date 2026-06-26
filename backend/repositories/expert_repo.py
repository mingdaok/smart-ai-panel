import uuid
from backend.db.connection import get_db


class ExpertRepo:
    async def create_batch(self, room_id: str, experts_data: list[dict]) -> list[dict]:
        result = []
        async with get_db() as db:
            for data in experts_data:
                expert_id = str(uuid.uuid4())
                await db.execute(
                    """INSERT INTO experts (id, room_id, name, title, stance, color, role, position)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (expert_id, room_id, data["name"], data["title"], data["stance"],
                     data["color"], data["role"], data["position"])
                )
                result.append({**data, "id": expert_id, "room_id": room_id,
                               "current_status": "idle", "public_thought": ""})
            await db.commit()
        return result

    async def get_by_room(self, room_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM experts WHERE room_id = ? ORDER BY position", (room_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_state(self, expert_id: str, status: str, thought: str = "") -> None:
        async with get_db() as db:
            await db.execute(
                "UPDATE experts SET current_status = ?, public_thought = ? WHERE id = ?",
                (status, thought, expert_id)
            )
            await db.commit()
