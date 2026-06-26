from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class InsightItem(BaseModel):
    id: str
    type: Literal["consensus", "disagreement"]
    content: str


class InsightUpdateResponse(BaseModel):
    """SSE insight.update 事件模型"""
    consensus: list[InsightItem] = []
    disagreement: list[InsightItem] = []
    timestamp: datetime
