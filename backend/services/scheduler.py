# backend/services/scheduler.py
# Scheduler service — core discussion scheduling and scoring engine
import asyncio
import logging
import random
import re
import time

from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo
from backend.repositories.room_repo import RoomRepo
from backend.services.sse_manager import sse_manager
from backend.services.mock_llm import MockLLMClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword marker sets for Chinese-language stance analysis
# ---------------------------------------------------------------------------
_OPPOSING_MARKERS = [
    "反对", "不", "质疑", "警惕", "过分", "过度", "自由", "自律",
    "市场", "行业自律", "担忧", "风险", "不应", "切勿", "不宜",
    "拒绝", "抵制", "否决",
]
_SUPPORTING_MARKERS = [
    "支持", "推进", "加强", "必须", "应该", "监管", "规范",
    "立法", "限制", "管控", "政府", "强制", "保障", "确立",
    "要求", "应当",
]


class Scheduler:
    COOLDOWN_SECONDS = 30
    MAX_ROUNDS = 12
    CONTEXT_MAX_LINES = 15
    SPEAK_THRESHOLD = 0.60
    W1 = 0.40  # relevance
    W2 = 0.35  # contrarian
    W3 = 0.20  # cooldown
    W4 = 0.05  # noise

    def __init__(self):
        self.llm = MockLLMClient()
        self._room_stop_flags: dict[str, bool] = {}

    async def _get_expert_states(self, room_id: str) -> dict[str, str]:
        """Return current_status for every expert in the given room."""
        repo = ExpertRepo()
        experts = await repo.get_by_room(room_id)
        return {e["id"]: e["current_status"] for e in experts}

    @staticmethod
    def _extract_cjk_keywords(text: str) -> set[str]:
        """Extract CJK character sequences as keyword tokens from text."""
        if not text:
            return set()
        # Match sequences of CJK Unified Ideographs (U+4E00 – U+9FFF)
        # plus common punctuation-free contiguous runs
        tokens = re.findall(r'[一-鿿]+', text)
        return set(tokens)

    @staticmethod
    def _is_opposing_stance(stance: str) -> bool:
        """Check if a stance text contains opposing/contrarian markers."""
        if not stance:
            return False
        return any(m in stance for m in _OPPOSING_MARKERS)

    @staticmethod
    def _is_supporting_content(content: str) -> bool:
        """Check if content text contains supporting/pro-regulation markers."""
        if not content:
            return False
        return any(m in content for m in _SUPPORTING_MARKERS)

    def _score_experts(self, experts: list[dict], last_content: str,
                       last_speak_times: dict[str, float]) -> dict:
        """
        Score all experts for next-speaker selection.

        Scoring formula (per plan):
            score = w1 * relevance + w2 * contrarian_bias
                    - w3 * cooldown_penalty + w4 * random.uniform(0, 0.2)

        relevance       = 0.3 + 0.7 * overlap_ratio  (keyword overlap between
                          stance and last_content)
        contrarian_bias = 0.8 if opposing_stance detected else 0.3
        cooldown_penalty= max(0, 1.0 - seconds_since / COOLDOWN_SECONDS)
        noise           = random.uniform(0, 0.2)

        Returns: dict[expert_id -> {score, relevance, contrarian_bias,
                  cooldown_penalty}]
        """
        now = time.time()
        result = {}

        # Pre-compute content CJK tokens once
        content_tokens = self._extract_cjk_keywords(last_content)
        content_is_supporting = self._is_supporting_content(last_content)

        for expert in experts:
            if expert.get("role") == "host":
                continue

            stance = expert.get("stance", "")

            # ---- relevance: Chinese keyword overlap between stance and content ----
            stance_tokens = self._extract_cjk_keywords(stance)
            if stance_tokens or content_tokens:
                overlap = len(stance_tokens & content_tokens)
                union = len(stance_tokens | content_tokens)
                overlap_ratio = overlap / max(union, 1)
            else:
                overlap_ratio = 0.0
            relevance = 0.3 + 0.7 * overlap_ratio  # range [0.3, 1.0]

            # ---- contrarian_bias: opposing stance vs supporting content ----
            is_opposing = self._is_opposing_stance(stance)
            contrarian_bias = 0.8 if (is_opposing and content_is_supporting) else 0.3

            # ---- cooldown_penalty: decay based on time since last speak ----
            last_time = last_speak_times.get(expert["id"], 0)
            if last_time > 0:
                seconds_since = now - last_time
                cooldown_penalty = max(0.0, 1.0 - seconds_since / self.COOLDOWN_SECONDS)
            else:
                cooldown_penalty = 0.0

            # ---- noise: small random factor to break ties ----
            noise = random.uniform(0, 0.2)

            score = (
                self.W1 * relevance
                + self.W2 * contrarian_bias
                - self.W3 * cooldown_penalty
                + self.W4 * noise
            )

            result[expert["id"]] = {
                "score": max(0.0, score),
                "relevance": relevance,
                "contrarian_bias": contrarian_bias,
                "cooldown_penalty": cooldown_penalty,
            }

        return result

    async def _select_next_speaker(self, room_id: str, round_num: int,
                                   last_speaker_id: str | None) -> dict | None:
        """
        Select the next speaker using the scoring engine.

        - Round 0: host always speaks first.
        - Round > 0: score all experts, pick the one with the highest score
          above SPEAK_THRESHOLD (0.60).
        - If no expert scores above the threshold, return None (host should
          step in).

        Returns a dict of expert data, or None if no suitable speaker is found.
        """
        repo = ExpertRepo()
        experts = await repo.get_by_room(room_id)

        # Round 0: host always opens
        if round_num == 0:
            hosts = [e for e in experts if e["role"] == "host"]
            return hosts[0] if hosts else None

        # Build last_speak_times from transcript history
        transcript_repo = TranscriptRepo()
        lines = await transcript_repo.get_by_room(room_id)
        last_speak_times: dict[str, float] = {}
        for line in lines:
            # Use a timestamp-ordered approximation: later lines overwrite
            # earlier ones, so each expert gets their most recent speak time.
            last_speak_times[line["expert_id"]] = time.time()

        last_content = lines[-1]["content"] if lines else ""

        # Score only non-host experts
        expert_candidates = [e for e in experts if e["role"] == "expert"]
        if not expert_candidates:
            return None

        scores = self._score_experts(expert_candidates, last_content,
                                     last_speak_times)
        if not scores:
            return None

        # Pick the highest-scoring expert above threshold
        best_id, best_data = max(scores.items(), key=lambda kv: kv[1]["score"])
        if best_data["score"] < self.SPEAK_THRESHOLD:
            return None  # No one wants to speak — host should intervene

        # Resolve best expert object
        for e in expert_candidates:
            if e["id"] == best_id:
                return e
        return None

    def _build_context(self, transcript: list[dict],
                       current_expert_stance: str) -> str:
        """
        Build a context string suitable for an LLM prompt.

        - Keeps only the last CONTEXT_MAX_LINES lines.
        - Formats each line as: "【{speaker_name}】: {content}"
        - Prepends a stance hint if provided.

        Returns a formatted context string.
        """
        recent = transcript[-self.CONTEXT_MAX_LINES:] if transcript else []

        parts: list[str] = []
        if current_expert_stance:
            parts.append(f"[当前发言人立场: {current_expert_stance}]")

        for line in recent:
            name = line.get("name", line.get("expert_name", "未知发言人"))
            content = line.get("content", "")
            parts.append(f"【{name}】: {content}")

        return "\n".join(parts)

    async def _extract_insights(self, transcript_text):
        """
        Stub: delegates to LLM client. Will be exercised with mock in tests.
        """
        return self.llm.generate_insights(transcript_text)

    async def _broadcast(self, room_id, event_type, data):
        """Stub: forward to SSEManager singleton."""
        await sse_manager.broadcast(room_id, event_type, data)

    async def _run_discussion(self, room_id: str):
        """
        Stub -- no-op. Full discussion loop will be implemented in Task 15.
        """
        pass

    async def start(self, room_id: str):
        """Stub: flag room as running and spawn discussion task."""
        self._room_stop_flags[room_id] = False
        asyncio.create_task(self._run_discussion(room_id))

    async def stop(self, room_id: str):
        """Stub: flag room to stop."""
        self._room_stop_flags[room_id] = True
