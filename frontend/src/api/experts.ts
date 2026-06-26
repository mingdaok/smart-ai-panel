import { api } from './client';
import type { ExpertResponse } from './rooms';

interface ExpertGenerationResponse {
  host: ExpertResponse;
  experts: ExpertResponse[];
  fallback?: boolean;
}

export function generateExperts(roomId: string) {
  return api.post<ExpertGenerationResponse>(
    `/api/rooms/${roomId}/experts`,
    { user_confirmed: false },
  );
}
