# Task 10 Report: POST /api/rooms/:id/experts Endpoint

**Status:** COMPLETED
**Date:** 2026-06-26
**TDD Cycle:** RED → GREEN → Commit

## Summary

Implemented the `POST /api/rooms/{room_id}/experts` endpoint following strict TDD.

## Files Created/Modified

### Created: `backend/routes/experts.py`
- `router` with prefix `/api/rooms`, tag `experts`
- Single endpoint: `POST /{room_id}/experts`
- Checks room exists → 404 if not
- Checks experts not already generated → 409 if they were
- Calls `MockLLMClient().generate_experts(topic, count)`
- Assigns colors from `EXPERT_COLORS` list (`#6366f1` through `#06b6d4`)
- Host gets `#f8fafc` always
- Expert i gets `EXPERT_COLORS[i % len(EXPERT_COLORS)]`
- Uses `ExpertRepo.create_batch()` to save
- Updates room status to "ready"
- Returns `{"host": {...}, "experts": [...]}`

### Created: `tests/test_api_experts.py`
- 3 test cases following the same file pattern as `test_api_rooms.py`
- Uses temporary file-based DB + cleanup fixture

### Modified: `backend/main.py`
- Added `from backend.routes.experts import router as experts_router`
- Added `app.include_router(experts_router)`

## Test Results

```
tests/test_api_experts.py::test_generate_experts PASSED
tests/test_api_experts.py::test_regenerate_returns_409 PASSED
tests/test_api_experts.py::test_experts_nonexistent_room PASSED
```

Full test suite: **40 passed** (no regressions)

## Test Cases

1. **test_generate_experts**: Creates a room, calls the experts endpoint, verifies 200 response with `host` and `experts` keys, correct expert count, host has role "host"
2. **test_regenerate_returns_409**: Generates experts once, then tries again → 409 Conflict
3. **test_experts_nonexistent_room**: Calls endpoint on nonexistent room ID → 404 Not Found

## Commit

```
1bc4971 feat: POST /api/rooms/:id/experts endpoint with LLM mock
```

## Design Decisions

- Uses `EXPERT_COLORS` as a module-level constant (not a constant per-request) for simplicity
- Host color `#f8fafc` is hardcoded as specified
- Room status transition: `waiting` → `ready` (after experts are generated)
- The endpoint accepts `ExpertGenerationRequest` body (with `user_confirmed: bool`) as defined in the model, though the flag is not yet acted upon (per spec, it's a placeholder for future use)
