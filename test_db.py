import asyncio
import sys
sys.path.append('.')
from backend.repositories.room_repo import RoomRepo
from backend.db.connection import init_db

async def main():
    await init_db()
    repo = RoomRepo()
    try:
        res = await repo.create({'topic': 'test', 'expert_count': 4})
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
