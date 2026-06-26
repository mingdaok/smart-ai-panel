# Task 18 Report: Frontend API Client Layer

**Status:** Complete
**Commit:** `07736f6` — `feat: frontend API client layer with typed fetch wrapper`

## Files Created

| File | Purpose |
|------|---------|
| `frontend/src/api/client.ts` | Generic `api.get<T>()` and `api.post<T>()` wrappers around `fetch` |
| `frontend/src/api/rooms.ts` | `createRoom()`, `listRooms()`, `getRoomDetail()` with typed interfaces |
| `frontend/src/api/experts.ts` | `generateExperts()` with `ExpertGenerationResponse` type |
| `frontend/src/api/discussion.ts` | `startDiscussion()`, `stopDiscussion()` |

## Verification

- `npx tsc --noEmit` — passed (zero errors)
- `npx vitest run` — 20 existing tests pass (2 test files, no regressions)

## Key Details

- Base URL: `http://localhost:3000`
- All requests set `Content-Type: application/json`
- Non-2xx responses throw `new Error(error.detail || 'HTTP {status}')`
- All functions return typed Promises via generics on `api.get<T>` / `api.post<T>`
- Shared interfaces (`RoomResponse`, `RoomDetail`, `ExpertResponse`) exported from `rooms.ts` and imported by `experts.ts` via `import type`
