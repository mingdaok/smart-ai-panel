# Task 19 Report: Frontend useSSE Hook

**Status:** COMPLETED

## File Created

- `frontend/src/hooks/useSSE.ts` — SSE hook with EventSource, auto-reconnect, event dispatch to Zustand stores

## What was implemented

The `useSSE` hook provides:

1. **SSE Connection**: Connects to `SSE_BASE/api/rooms/:roomId/stream` using native `EventSource`.
2. **Event Dispatch**: Listens for 5 event types and dispatches to the corresponding Zustand stores:
   - `room.status` -> `updateRoomStatus(room_id, status)`
   - `expert.state` -> `updateExpertState(expert_id, status, public_thought)`
   - `transcript.line` -> `addLine(data)`
   - `insight.update` -> `updateInsights(consensus, disagreement)`
   - `discussion.end` -> `updateRoomStatus(roomId, 'finished')`
3. **Auto-Reconnect**: On `onerror`, closes the EventSource and reconnects with exponential backoff (2s * 2^attempt, max 30s, up to 5 attempts).
4. **Reset on Open**: `onopen` resets `reconnectCount` to 0.
5. **Cleanup**: `useEffect` cleanup closes the EventSource on unmount.
6. **Public API**: Returns `{ connect, disconnect }` callbacks.

## Constants

- `SSE_BASE = 'http://localhost:3000'`
- `MAX_RECONNECT_ATTEMPTS = 5`

## Verification

- `cd frontend && npx tsc --noEmit` — PASSED (0 errors)
