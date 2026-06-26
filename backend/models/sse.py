from enum import StrEnum
from pydantic import BaseModel
from datetime import datetime
from backend.models.room import RoomStatus
from backend.models.expert import ExpertStatus


class SSEEventType(StrEnum):
    ROOM_STATUS = "room.status"
    EXPERT_STATE = "expert.state"
    TRANSCRIPT_LINE = "transcript.line"
    INSIGHT_UPDATE = "insight.update"
    DISCUSSION_END = "discussion.end"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class SSERoomStatus(BaseModel):
    room_id: str
    status: RoomStatus
    timestamp: datetime


class SSEExpertState(BaseModel):
    expert_id: str
    name: str
    status: ExpertStatus
    public_thought: str
    timestamp: datetime


class SSEDiscussionEnd(BaseModel):
    summary: str
    total_rounds: int
    final_consensus: list[str] = []
    final_disagreement: list[str] = []


class SSEError(BaseModel):
    code: str
    message: str
    recoverable: bool = False
