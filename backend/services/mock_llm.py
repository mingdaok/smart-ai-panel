# backend/services/mock_llm.py
import asyncio
import random
from backend.models.expert import LLMExpertRaw, LLMExpertsResponse

FALLBACK_TEMPLATES = {
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
        await asyncio.sleep(1)
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
        await asyncio.sleep(1.5)  # Simulate LLM streaming delay
        speeches = {
            "argument": [
                f"站在{stance}的角度，我认为当前最大的问题被忽视了。",
                f"我必须指出，目前的趋势令人担忧，我们需要更长远的目光。",
                f"数据不会说谎，结合历史经验，这个方案的风险大于收益。",
                f"实际上，这是技术演进的必经之路，我们不能因噎废食。"
            ],
            "rebuttal": [
                f"我完全不能苟同刚才的观点。从{stance}来看，这明显是谬误。",
                f"刚才的说法太过于理想化了，在实际操作中根本行不通。",
                f"我反驳一下，核心逻辑其实是有漏洞的。"
            ],
            "supplement": [
                f"除了刚才提到的，我还要补充一点：我们需要考虑到社会层面的影响。",
                f"确实如此，而且顺着这个思路，我们还能发现更多机会。"
            ],
            "question": [
                f"在继续推进之前，我想请问各位：我们是否低估了潜在的道德风险？",
                f"谁来为这个结果买单？这是一个不可回避的问题。"
            ],
            "opening": [
                "欢迎各位来到今天的圆桌讨论，让我们直奔主题。"
            ],
            "closing": [
                "今天的讨论非常深刻，虽然未达成绝对共识，但碰撞出的火花非常有价值。感谢各位！"
            ],
        }
        options = speeches.get(line_type, speeches["argument"])
        return random.choice(options)

    async def generate_insights(self, transcript_snippet: str) -> dict:
        await asyncio.sleep(1)
        return {
            "consensus": [
                "大家都承认这是一项极具破坏性的变革",
                "对相关法律法规的完善迫在眉睫"
            ],
            "disagreement": [
                "对于是否应该采取保守策略存在极大分歧",
                "在风险可控性的评估上，各方标准不一"
            ]
        }

    async def generate_public_thought(self, expert_name: str, stance: str) -> str:
        await asyncio.sleep(0.5)
        thoughts = [
            f"正在结合立场迅速组织反击论点...",
            "在倾听并寻找逻辑漏洞...",
            "准备抛出一个尖锐的质问...",
            "正在翻阅相关历史数据进行对比...",
        ]
        return random.choice(thoughts)
