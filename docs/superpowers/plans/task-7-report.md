# Task 7 Report: TranscriptLine & Insight Repositories

**Status:** COMPLETE -- All 24 tests passing

## Summary

Implemented `TranscriptRepo` and `InsightRepo` data access layer classes following strict TDD (RED -> GREEN -> COMMIT).

## TDD Cycle

### RED Phase
- Wrote `tests/test_transcript_insight_repo.py` with 2 test cases
- `test_add_and_get_transcript`: Creates a room and expert, adds a transcript line, verifies content/type/retrieval
- `test_add_and_get_insights`: Creates a room, adds consensus + disagreement insights, verifies retrieval order
- Verified RED: `ModuleNotFoundError: No module named 'backend.repositories.transcript_repo'`

### GREEN Phase
- Created `backend/repositories/transcript_repo.py` with `TranscriptRepo` class:
  - `add(data) -> dict`: Inserts into `transcript_lines` table, returns enriched dict
  - `get_by_room(room_id) -> list[dict]`: JOINS with `experts` table to include name, title, color
- Created `backend/repositories/insight_repo.py` with `InsightRepo` class:
  - `add(room_id, type_, content) -> dict`: Inserts into `insights` table, returns full record
  - `get_by_room(room_id) -> list[dict]`: Returns insights ordered by `updated_at`
- Updated `backend/repositories/__init__.py` to export all repos

### Prerequisite
- Created `backend/repositories/expert_repo.py` (Task 6 dependency) with `create_batch`, `get_by_room`, `update_state`

### Verification
- 2/2 new tests pass
- 24/24 total test suite passes

## Files Changed
- `backend/repositories/expert_repo.py` (created - prerequisite)
- `backend/repositories/transcript_repo.py` (created)
- `backend/repositories/insight_repo.py` (created)
- `backend/repositories/__init__.py` (modified - added exports)
- `tests/test_transcript_insight_repo.py` (created)

## Technical Note
The plan specified using `DB_PATH.set(tempfile_path)` with an autouse async fixture, but `pytest-asyncio` on Python 3.14 does not support autouse async fixtures without special configuration. Adapted to use a sync cleanup fixture + inline `DB_PATH.set()` / `await init_db()` calls in each test body, consistent with the existing `test_room_repo.py` pattern.
