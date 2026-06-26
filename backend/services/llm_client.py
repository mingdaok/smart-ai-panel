# backend/services/llm_client.py
# Real Deepseek API integration — OpenAI SDK compatible.

import asyncio
import json
import logging
from openai import AsyncOpenAI
from backend.config import get_settings
from backend.models.expert import LLMExpertRaw, LLMExpertsResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates — kept inline for MVP, can extract to .txt files later
# ---------------------------------------------------------------------------

GEN_EXPERTS_SYSTEM = """You are a discussion-moderator generator. Given a topic and a desired number of experts, generate a host and a panel of experts with diverse stances spanning from strongly supportive to strongly opposing.

Return ONLY valid JSON, no markdown, no extra text. The JSON must have exactly this structure:
{
  "host": { "name": "主持人姓名", "title": "头衔", "stance": "中立客观的立场描述" },
  "experts": [
    { "name": "专家姓名", "title": "头衔", "stance": "鲜明的个人立场描述" },
    ...
  ]
}

RULES:
- Host position is neutral, guides discussion, does NOT take sides.
- Expert stances MUST cover the full spectrum: at least one strongly supportive, one strongly opposing, and one neutral/pragmatic.
- All names should be realistic Chinese names (2-3 characters for surnames, 2-3 characters total if possible, but can use full names like 张明).
- All titles should be specific and realistic (e.g., "AI 伦理研究员", "科技政策顾问", "数据科学家").
- Every stance must be a full sentence describing their position, NOT a single word.
- Use Chinese for all content.
"""

GEN_SPEECH_SYSTEM = """You are an expert panelist in a roundtable discussion. You will be given your persona (name, stance, title) and the recent discussion context. Generate a single short speech.

RULES:
- Speak in first-person ("我认为...", "我的观点是...").
- Keep it to 1-2 sentences, concise and punchy.
- Stay firmly in character — your stance drives everything you say.
- If your line_type is "rebuttal", directly challenge the previous speaker's point.
- If "supplement", add a new angle without repeating what was said.
- If "question", ask a sharp, provocative question.
- If "opening", introduce the topic from your perspective.
- If "closing", summarize the key points and thank everyone.
- NEVER output JSON or markdown. Output plain Chinese text only.
- NEVER use <thinking> tags or any hidden chain-of-thought markers.
"""

GEN_INSIGHT_SYSTEM = """You are a discussion analyst. Given recent transcript lines, extract new consensus and disagreement points.

Return ONLY valid JSON:
{
  "consensus": ["共识点1", "共识点2", ...],
  "disagreement": ["分歧点1", ...]
}

RULES:
- Only extract points that are genuinely new (not already obvious from the topic).
- Consensus = positions that multiple experts explicitly agree on.
- Disagreement = positions where experts explicitly contradict each other.
- If there are no new consensus or disagreement points, return empty lists.
- Use Chinese. Maximum 3 items per category.
"""

GEN_THOUGHT_SYSTEM = """You are an expert in a roundtable discussion. Given your persona, generate a short (<15 Chinese characters) public thought that reflects your current thinking state.

This is NOT your speech. This is your internal monologue visible to the audience. Do NOT reveal hidden chain-of-thought. Keep it natural and human-like (e.g., "正在重新审视这个论点...", "注意到一个关键漏洞").

Return plain Chinese text only, no JSON, no markdown, under 15 characters."""

# ---------------------------------------------------------------------------
# Expert color palette (matches Design Tokens)
# ---------------------------------------------------------------------------
EXPERT_COLORS = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#8b5cf6", "#06b6d4"]


class RealLLMClient:
    """Real Deepseek API client — OpenAI SDK compatible interface."""

    def __init__(self):
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self._timeout = settings.llm_timeout
        self._model = "deepseek-chat"  # Deepseek V3/V4 chat model

    async def _chat(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        """Send a chat completion request. Returns the response text."""
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self._timeout,
        )
        return resp.choices[0].message.content

    # ---- Public interface (mirrors MockLLMClient) ----

    async def generate_experts(self, topic: str, count: int) -> "LLMExpertsResponse":
        """Call Deepseek to generate host + expert lineup, with Pydantic validation + retry + fallback."""
        from backend.services.mock_llm import MockLLMClient
        from pydantic import ValidationError

        user = f"话题: {topic}\n需要的专家人数: {count}"

        for attempt in range(3):
            try:
                raw = await self._chat(GEN_EXPERTS_SYSTEM, user, temperature=0.9, max_tokens=1024)
                return LLMExpertsResponse.model_validate_json(raw)
            except (ValidationError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f"LLM expert generation validation failed (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    await asyncio.sleep(0.5)
                # Fall through to fallback on last attempt

        # Silent fallback — return Mock data, marked with fallback=True
        logger.warning(f"LLM expert generation failed after 3 retries — using fallback lineup")
        mock = MockLLMClient()
        result = mock.generate_experts(topic, count)
        return result

    async def generate_speech(self, expert_name: str, stance: str, context: str, line_type: str) -> str:
        """Call Deepseek to generate an expert's speech."""
        user = (
            f"你的名字: {expert_name}\n"
            f"你的立场: {stance}\n"
            f"发言类型: {line_type}\n"
            f"近期讨论上下文:\n{context}\n\n"
            f"请以 {expert_name} 的身份发表一段简短的发言:"
        )
        return await self._chat(GEN_SPEECH_SYSTEM, user, temperature=0.8, max_tokens=256)

    async def generate_insights(self, transcript_snippet: str) -> dict:
        """Call Deepseek to extract consensus and disagreement."""
        user = f"近期讨论记录:\n{transcript_snippet}"
        for attempt in range(3):
            try:
                raw = await self._chat(GEN_INSIGHT_SYSTEM, user, temperature=0.5, max_tokens=256)
                return json.loads(raw)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"LLM insight extraction failed (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    await asyncio.sleep(0.3)
        return {"consensus": [], "disagreement": []}

    async def generate_public_thought(self, expert_name: str, stance: str) -> str:
        """Call Deepseek to generate a public thought summary."""
        user = f"你的名字: {expert_name}\n你的立场: {stance}\n请表达你当前的真实想法（<15字）:"
        try:
            thought = await self._chat(GEN_THOUGHT_SYSTEM, user, temperature=0.9, max_tokens=50)
            return thought.strip()[:30]  # safety cap
        except Exception as e:
            logger.warning(f"LLM thought generation failed: {e}")
            return "正在思考中..."
