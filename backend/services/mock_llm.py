# backend/services/mock_llm.py
from backend.models.expert import LLMExpertRaw, LLMExpertsResponse

FALLBACK_TEMPLATES = {
    "tech": {
        "host": {"name": "陈博士", "title": "圆桌主持人", "stance": "中立客观"},
        "experts": [
            {"name": "张总", "title": "科技企业家", "stance": "坚信技术创新是第一生产力，支持自由发展"},
            {"name": "王教授", "title": "AI 伦理学家", "stance": "技术必须以人类福祉为前提，支持严格监管"},
            {"name": "李工", "title": "一线AI工程师", "stance": "从技术可行性角度理性分析问题"},
            {"name": "赵观察员", "title": "独立科技评论员", "stance": "关注产业生态平衡，偏向市场调节"},
        ]
    },
    "generic": {
        "host": {"name": "陈博士", "title": "资深圆桌主持人", "stance": "中立客观，引导讨论"},
        "experts": [
            {"name": "张教授", "title": "乐观派学者", "stance": "强烈支持并推动该议题的积极方向"},
            {"name": "王老师", "title": "批判性思考者", "stance": "持怀疑态度，质疑过于乐观的假设"},
            {"name": "李分析师", "title": "数据驱动分析师", "stance": "依据数据和实证评估各方论点"},
            {"name": "赵先生", "title": "务实主义者", "stance": "关注实际可行性和落地难度"},
        ]
    }
}

class MockLLMClient:
    async def generate_experts(self, topic: str, count: int) -> LLMExpertsResponse:
        template = FALLBACK_TEMPLATES["generic"]
        experts = template["experts"][:count]
        # Pad if more experts needed than template has
        while len(experts) < count:
            experts.append({"name": f"专家{len(experts)+1}", "title": "特邀嘉宾", "stance": f"立场视角{len(experts)+1}"})
        return LLMExpertsResponse(
            host=LLMExpertRaw(**template["host"]),
            experts=[LLMExpertRaw(**e) for e in experts[:count]]
        )

    async def generate_speech(self, expert_name: str, stance: str, context: str, line_type: str) -> str:
        speeches = {
            "argument": f"{expert_name}认为，基于{stance}的立场，这个问题需要更深入的探讨。",
            "rebuttal": f"{expert_name}反驳道：从前面的发言来看，有一些关键点被忽略了。",
            "supplement": f"{expert_name}补充说：还有一个角度值得考虑。",
            "question": f"{expert_name}提出疑问：我们是否应该重新审视这个前提？",
            "opening": "欢迎各位来到今天的圆桌讨论。让我们围绕这个话题展开深度对话。",
            "closing": "今天的讨论非常精彩，感谢各位专家贡献的深刻洞见。",
        }
        return speeches.get(line_type, speeches["argument"])

    async def generate_insights(self, transcript_snippet: str) -> dict:
        return {
            "consensus": ["各方都认识到该议题的重要性"],
            "disagreement": ["在具体实施方案上存在分歧"]
        }

    async def generate_public_thought(self, expert_name: str, stance: str) -> str:
        thoughts = [
            f"正在从{stance}的角度分析...",
            "正在组织论点...",
            "关注当前讨论的走向...",
            "准备回应前一个观点...",
        ]
        import random
        return random.choice(thoughts)
