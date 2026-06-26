from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

RoomStatus = Literal["waiting", "generating", "ready", "discussing", "finished", "stopped"]


class RoomCreate(BaseModel):
    """POST /api/rooms Request"""
    topic: str = Field(..., min_length=1, max_length=200, description="讨论议题")
    expert_count: int = Field(default=4, ge=2, le=8, description="专家人数")


class RoomResponse(BaseModel):
    """GET /api/rooms Response Item"""
    id: str
    topic: str
    expert_count: int
    status: RoomStatus
    created_at: datetime
    updated_at: datetime


class RoomDetail(RoomResponse):
    """GET /api/rooms/{id} Response -- 含完整阵容和统计"""
    experts: list["ExpertResponse"] = []
    transcript_count: int = 0
    insight_count: int = 0


from backend.models.expert import ExpertResponse
RoomDetail.model_rebuild()
