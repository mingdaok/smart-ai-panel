# tests/test_mock_llm.py
import pytest
from backend.services.mock_llm import MockLLMClient
from backend.models.expert import LLMExpertsResponse

class TestMockLLMClient:
    def test_generate_experts_returns_valid_structure(self):
        client = MockLLMClient()
        result = client.generate_experts("AI 监管", 4)
        assert isinstance(result, LLMExpertsResponse)
        assert result.host.name
        assert result.host.title
        assert len(result.experts) == 4
        # All experts have distinct stances
        stances = [e.stance for e in result.experts]
        assert len(set(stances)) == 4

    def test_generate_experts_different_counts(self):
        client = MockLLMClient()
        for n in [2, 5, 8]:
            result = client.generate_experts("测试话题", n)
            assert len(result.experts) == n

    def test_generate_speech_returns_string(self):
        client = MockLLMClient()
        speech = client.generate_speech(
            expert_name="张教授", stance="支持监管",
            context="当前讨论监管必要性", line_type="argument"
        )
        assert isinstance(speech, str)
        assert len(speech) > 0

    def test_generate_insights_returns_consensus_and_disagreement(self):
        client = MockLLMClient()
        result = client.generate_insights("张教授认为需要监管，李总认为行业自律更有效")
        assert "consensus" in result
        assert "disagreement" in result
