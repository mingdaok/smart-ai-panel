# backend/services/scheduler.py
# Stub — TDD RED Phase (Task 13). Logic will be implemented in Task 14.
import asyncio
import logging
import random
import time

from backend.repositories.expert_repo import ExpertRepo
from backend.repositories.transcript_repo import TranscriptRepo
from backend.repositories.insight_repo import InsightRepo
from backend.repositories.room_repo import RoomRepo
from backend.services.sse_manager import sse_manager
from backend.services.mock_llm import MockLLMClient

logger = logging.getLogger(__name__)


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

    # ------------------------------------------------------------------
    # Stub methods — return minimal valid structures so tests compile
    # ------------------------------------------------------------------

    async def _get_expert_states(self, room_id: str) -> dict[str, str]:
        """Return current_status for every expert in the given room."""
        repo = ExpertRepo()
        experts = await repo.get_by_room(room_id)
        return {e["id"]: e["current_status"] for e in experts}

    def _score_experts(self, experts, last_content, last_speak_times):
        """
        Stub scoring: assigns random scores with deterministic biases
        so TC-SCH-02/03/04 can exercise the structure without real logic.

        Returns: dict[expert_id -> {score, relevance, contrarian_bias, cooldown_penalty}]
        """
        result = {}
        for expert in experts:
            if expert["role"] == "host":
                continue
            # Deterministic placeholder values so tests can assert on them
            stance = expert.get("stance", "")
            # Give a slight contrarian bump if stance contains "反对"
            contrarian_bias = 0.8 if "反对" in stance else 0.3
            # Slight relevance bump if stance shares keywords with content
            relevance = 0.6
            if last_content and stance:
                if any(kw in stance for kw in ["支持", "监管", "安全"]):
                    relevance = 0.7
            # Cooldown penalty: proportional to how recently the expert spoke
            now = time.time()
            last_time = last_speak_times.get(expert["id"], 0)
            cooldown_penalty = 0.0
            if last_time > 0:
                seconds_since = now - last_time
                if seconds_since < self.COOLDOWN_SECONDS:
                    cooldown_penalty = max(0.0, 1.0 - seconds_since / self.COOLDOWN_SECONDS)
            # Small noise factor
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
                                   last_speaker_id: str | None):
        """
        Stub speaker selection:
        - round 0: return host
        - otherwise: return first expert (naive — will be upgraded in Task 14)
        """
        repo = ExpertRepo()
        experts = await repo.get_by_room(room_id)
        if round_num == 0:
            hosts = [e for e in experts if e["role"] == "host"]
            if hosts:
                return hosts[0]
            return None
        # Non-round-0: return first non-host expert
        non_hosts = [e for e in experts if e["role"] != "host"]
        return non_hosts[0] if non_hosts else None

    def _build_context(self, transcript, current_expert_stance):
        """
        Stub context builder: takes the last CONTEXT_MAX_LINES lines
        and concatenates their content.
        """
        lines = transcript[-self.CONTEXT_MAX_LINES:]
        return " ".join(l["content"] for l in lines)

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
        Stub — no-op. Full discussion loop will be implemented in Task 14.
        """
        pass  # TODO: implement in Task 14

    async def start(self, room_id: str):
        """Stub: flag room as running and spawn discussion task."""
        self._room_stop_flags[room_id] = False
        asyncio.create_task(self._run_discussion(room_id))

    async def stop(self, room_id: str):
        """Stub: flag room to stop."""
        self._room_stop_flags[room_id] = True
