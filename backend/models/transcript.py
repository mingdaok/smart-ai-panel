from pydantic import BaseModel
from typing import Literal
from datetime import datetime

LineType = Literal["opening", "argument", "rebuttal", "supplement", "question", "closing"]


class TranscriptLineResponse(BaseModel):
    """SSE transcript.line 事件 + REST 响应 统一的字幕行模型"""
    id: str
    expert_id: str
    name: str
    title: str
    color: str
    content: str
    line_type: LineType
    sequence_num: int
    created_at: datetime
