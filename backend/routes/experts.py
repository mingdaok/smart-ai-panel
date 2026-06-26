from fastapi import APIRouter, HTTPException
from backend.models.expert import ExpertGenerationRequest
from backend.repositories.room_repo import RoomRepo
from backend.repositories.expert_repo import ExpertRepo
from backend.services.mock_llm import MockLLMClient

router = APIRouter(prefix="/api/rooms", tags=["experts"])

EXPERT_COLORS = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#8b5cf6", "#06b6d4"]


@router.post("/{room_id}/experts")
async def generate_experts(room_id: str, body: ExpertGenerationRequest):
    room_repo = RoomRepo()
    room = await room_repo.get_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    expert_repo = ExpertRepo()
    existing = await expert_repo.get_by_room(room_id)
    if existing:
        raise HTTPException(status_code=409, detail="Experts already generated for this room")

    llm = MockLLMClient()
    result = llm.generate_experts(room["topic"], room["expert_count"])

    experts_data = []
    # Host first
    experts_data.append({
        "name": result.host.name, "title": result.host.title, "stance": result.host.stance,
        "color": "#f8fafc", "role": "host", "position": 0
    })
    for i, e in enumerate(result.experts):
        experts_data.append({
            "name": e.name, "title": e.title, "stance": e.stance,
            "color": EXPERT_COLORS[i % len(EXPERT_COLORS)], "role": "expert", "position": i + 1
        })

    created = await expert_repo.create_batch(room_id, experts_data)
    await room_repo.update_status(room_id, "ready")

    host = [e for e in created if e["role"] == "host"][0]
    experts = [e for e in created if e["role"] == "expert"]
    return {"host": host, "experts": experts}
