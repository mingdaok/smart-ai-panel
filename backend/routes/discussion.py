from fastapi import APIRouter, HTTPException
from backend.repositories.room_repo import RoomRepo
from backend.services.scheduler import Scheduler

router = APIRouter(prefix="/api/rooms", tags=["discussion"])
_schedulers: dict[str, Scheduler] = {}


@router.post("/{room_id}/start")
async def start_discussion(room_id: str):
    repo = RoomRepo()
    room = await repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["status"] != "ready":
        raise HTTPException(status_code=409, detail="Room is not in ready status")
    scheduler = Scheduler()
    _schedulers[room_id] = scheduler
    await scheduler.start(room_id)
    return {"stream_started": True, "room_id": room_id}


@router.post("/{room_id}/stop")
async def stop_discussion(room_id: str):
    repo = RoomRepo()
    room = await repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["status"] != "discussing":
        raise HTTPException(status_code=409, detail="Room is not in discussing status")
    scheduler = _schedulers.get(room_id)
    if scheduler:
        await scheduler.stop(room_id)
    await repo.update_status(room_id, "stopped")
    return {"stopped": True, "room_id": room_id}
