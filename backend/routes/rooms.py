from fastapi import APIRouter, HTTPException
from backend.models.room import RoomCreate, RoomResponse, RoomDetail
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.post("", status_code=201, response_model=RoomResponse)
async def create_room(body: RoomCreate):
    repo = RoomRepo()
    room = await repo.create({"topic": body.topic, "expert_count": body.expert_count})
    return RoomResponse(**room)


@router.get("")
async def list_rooms():
    repo = RoomRepo()
    rooms = await repo.list_all()
    return {"rooms": [RoomResponse(**r) for r in rooms]}


@router.get("/{room_id}", response_model=RoomDetail)
async def get_room(room_id: str):
    repo = RoomRepo()
    room = await repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    expert_repo = ExpertRepo()
    experts = await expert_repo.get_by_room(room_id)
    transcript_repo = TranscriptRepo()
    transcripts = await transcript_repo.get_by_room(room_id)
    insight_repo = InsightRepo()
    insights = await insight_repo.get_by_room(room_id)
    return RoomDetail(
        **room,
        experts=experts,
        transcript_count=len(transcripts),
        insight_count=len(insights),
    )
