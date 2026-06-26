from pydantic import BaseModel, Field
from typing import Literal

ExpertRole = Literal["host", "expert"]
ExpertStatus = Literal["idle", "preparing", "speaking"]


class ExpertResponse(BaseModel):
    """API 返回的专家信息 -- 前端永远通过此模型消费"""
    id: str
    name: str
    title: str
    stance: str
    color: str
    role: ExpertRole
    position: int
    current_status: ExpertStatus = "idle"
    public_thought: str = ""


class LLMExpertRaw(BaseModel):
    """LLM 返回的专家原始数据 -- Pydantic 严格反序列化防线"""
    name: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=50)
    stance: str = Field(..., min_length=1, max_length=100)


class LLMExpertsResponse(BaseModel):
    """POST /api/rooms/{id}/experts -- LLM 生成阵容的原始响应校验"""
    host: LLMExpertRaw
    experts: list[LLMExpertRaw] = Field(..., min_length=1, max_length=8)


class ExpertGenerationRequest(BaseModel):
    """触发阵容生成的请求体（可选确认标记）"""
    user_confirmed: bool = False
