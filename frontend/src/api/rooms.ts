import { api } from './client';

export interface RoomResponse {
  id: string;
  topic: string;
  expert_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface RoomDetail extends RoomResponse {
  experts: ExpertResponse[];
  transcript_count: number;
  insight_count: number;
}

export interface ExpertResponse {
  id: string;
  name: string;
  title: string;
  stance: string;
  color: string;
  role: 'host' | 'expert';
  position: number;
  current_status: 'idle' | 'preparing' | 'speaking';
  public_thought: string;
}

export function createRoom(topic: string, expert_count: number) {
  return api.post<RoomResponse>('/api/rooms', { topic, expert_count });
}

export function listRooms() {
  return api.get<{ rooms: RoomResponse[] }>('/api/rooms');
}

export function getRoomDetail(id: string) {
  return api.get<RoomDetail>(`/api/rooms/${id}`);
}
