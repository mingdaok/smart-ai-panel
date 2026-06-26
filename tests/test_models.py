import pytest
from pydantic import ValidationError
from backend.models.room import RoomCreate, RoomResponse, RoomDetail
from backend.models.expert import ExpertResponse, LLMExpertRaw, LLMExpertsResponse
from backend.models.transcript import TranscriptLineResponse
from backend.models.insight import InsightItem, InsightUpdateResponse
from backend.models.sse import SSEEventType, SSERoomStatus, SSEExpertState, SSEDiscussionEnd, SSEError
from datetime import datetime


class TestRoomCreate:
    def test_valid_room_create(self):
        rc = RoomCreate(topic="AI 监管", expert_count=4)
        assert rc.topic == "AI 监管"
        assert rc.expert_count == 4

    def test_topic_too_short(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="", expert_count=4)

    def test_topic_too_long(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="x" * 201, expert_count=4)

    def test_expert_count_min(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="Test", expert_count=1)

    def test_expert_count_max(self):
        with pytest.raises(ValidationError):
            RoomCreate(topic="Test", expert_count=9)


class TestLLMExpertRaw:
    def test_valid_expert(self):
        e = LLMExpertRaw(name="张教授", title="AI 研究员", stance="支持严格监管")
        assert e.name == "张教授"

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            LLMExpertRaw(name="x" * 21, title="研究员", stance="中立")


class TestLLMExpertsResponse:
    def test_valid_response(self):
        r = LLMExpertsResponse(
            host=LLMExpertRaw(name="主持人", title="圆桌主持", stance="中立客观"),
            experts=[LLMExpertRaw(name="专家A", title="研究员", stance="支持")]
        )
        assert len(r.experts) == 1

    def test_min_experts(self):
        with pytest.raises(ValidationError):
            LLMExpertsResponse(
                host=LLMExpertRaw(name="主持人", title="主持", stance="中立"),
                experts=[]
            )


class TestSSEEventType:
    def test_all_event_types(self):
        assert SSEEventType.ROOM_STATUS == "room.status"
        assert SSEEventType.EXPERT_STATE == "expert.state"
        assert SSEEventType.TRANSCRIPT_LINE == "transcript.line"
        assert SSEEventType.INSIGHT_UPDATE == "insight.update"
        assert SSEEventType.DISCUSSION_END == "discussion.end"
        assert SSEEventType.HEARTBEAT == "heartbeat"
        assert SSEEventType.ERROR == "error"
