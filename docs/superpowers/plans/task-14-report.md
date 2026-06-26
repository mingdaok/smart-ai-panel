# Task 14 Report: Scheduler -- GREEN Phase (Core Scoring Logic)

**Date:** 2026-06-26
**Status:** COMPLETE
**Tests:** 9 passed, 1 skipped (all pre-existing skips)

## Summary

Replaced the three stub methods in `backend/services/scheduler.py` with production-quality implementations:

1. `_score_experts()` -- real relevance, contrarian bias, cooldown penalty, and noise
2. `_select_next_speaker()` -- scoring-based selection with SPEAK_THRESHOLD check
3. `_build_context()` -- formatted for LLM prompt consumption

## Changes Made

### `_score_experts()` (lines 81-151)

Replaced the hardcoded-relevance + token-matching stub with:

- **Chinese keyword extraction:** `_extract_cjk_keywords()` uses `re.findall(r'[一-鿿]+', text)` to extract CJK character sequences as tokens
- **Relevance:** `0.3 + 0.7 * overlap_ratio` where `overlap_ratio` is Jaccard similarity between stance tokens and content tokens
- **Contrarian bias:** 0.8 if stance contains opposing markers AND content contains supporting markers, else 0.3
  - Opposing markers: 反对, 不, 质疑, 警惕, 过分, 过度, 自由, 自律, 市场, 行业自律, 担忧, 风险, 不应, 切勿, 不宜, 拒绝, 抵制, 否决
  - Supporting markers: 支持, 推进, 加强, 必须, 应该, 监管, 规范, 立法, 限制, 管控, 政府, 强制, 保障, 确立, 要求, 应当
- **Cooldown penalty:** `max(0, 1.0 - seconds_since / COOLDOWN_SECONDS)`
- **Noise:** `random.uniform(0, 0.2)`
- **Weighted formula:** `0.40 * relevance + 0.35 * contrarian_bias - 0.20 * cooldown_penalty + 0.05 * noise`

### `_select_next_speaker()` (lines 153-204)

- Round 0: returns host (unchanged)
- Round > 0: builds `last_speak_times` from transcript history, calls `_score_experts()` on all non-host experts, returns the highest-scoring expert above `SPEAK_THRESHOLD` (0.60)
- Returns `None` if no expert scores above threshold (host should step in)

### `_build_context()` (lines 206-228)

- Keeps last `CONTEXT_MAX_LINES` lines
- Formats as: `[当前发言人立场: {stance}]\n【{name}】: {content}\n...`
- Prepends stance hint when provided for LLM prompt awareness

## Test Results

```
tests/test_scheduler.py::test_experts_initial_state_idle PASSED
tests/test_scheduler.py::test_scoring_ranks_experts_by_relevance PASSED
tests/test_scheduler.py::test_cooldown_penalty_reduces_score PASSED
tests/test_scheduler.py::test_contrarian_bias_boosts_opposing_stance PASSED
tests/test_scheduler.py::test_host_speaks_first PASSED
tests/test_scheduler.py::test_discussion_ends_with_host_closing SKIPPED
tests/test_scheduler.py::test_context_window_respects_limit PASSED
tests/test_scheduler.py::test_insight_extractor_finds_consensus PASSED
tests/test_scheduler.py::test_insight_extractor_finds_disagreement PASSED
tests/test_scheduler.py::test_concurrent_rooms_have_isolated_schedulers PASSED
```

Full test suite: 49 passed, 4 skipped (no regressions).

## Stubs Remaining

- `_run_discussion()` -- still a no-op stub (to be implemented in Task 15)
- `_extract_insights()` -- delegates to LLM client (functional, exercised with mock)

## Commit

```
feat: scheduler scoring engine with real relevance, contrarian bias, and cooldown penalty
```
