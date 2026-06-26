import { api } from './client';

export function startDiscussion(roomId: string) {
  return api.post<{ stream_started: boolean; room_id: string }>(
    `/api/rooms/${roomId}/start`,
  );
}

export function stopDiscussion(roomId: string) {
  return api.post<{ stopped: boolean; room_id: string }>(
    `/api/rooms/${roomId}/stop`,
  );
}
