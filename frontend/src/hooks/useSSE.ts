// frontend/src/hooks/useSSE.ts
import { useEffect, useRef, useCallback } from 'react';
import { useRoomStore } from '../store/roomSlice';
import { useExpertStore } from '../store/expertSlice';
import { useTranscriptStore } from '../store/transcriptSlice';
import { useInsightStore } from '../store/insightSlice';

const SSE_BASE = 'http://localhost:3000';
const MAX_RECONNECT_ATTEMPTS = 5;

export function useSSE(roomId: string | null) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectCount = useRef(0);

  const updateRoomStatus = useRoomStore((s) => s.updateRoomStatus);
  const updateExpertState = useExpertStore((s) => s.updateExpertState);
  const addLine = useTranscriptStore((s) => s.addLine);
  const updateInsights = useInsightStore((s) => s.updateInsights);

  const connect = useCallback(() => {
    if (!roomId) return;
    
    if (eventSourceRef.current) {
        eventSourceRef.current.close();
    }

    const es = new EventSource(`${SSE_BASE}/api/rooms/${roomId}/stream`);
    eventSourceRef.current = es;

    es.addEventListener('room.status', (e) => {
      const data = JSON.parse(e.data);
      updateRoomStatus(data.room_id, data.status);
    });

    es.addEventListener('expert.state', (e) => {
      const data = JSON.parse(e.data);
      updateExpertState(data.expert_id, data.status, data.public_thought);
    });

    es.addEventListener('transcript.line', (e) => {
      const data = JSON.parse(e.data);
      addLine(data);
    });

    es.addEventListener('insight.update', (e) => {
      const data = JSON.parse(e.data);
      updateInsights(data.consensus, data.disagreement);
    });

    es.addEventListener('discussion.end', (e) => {
      const data = JSON.parse(e.data);
      updateRoomStatus(roomId, 'finished');
    });

    es.onerror = () => {
      es.close();
      if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectCount.current++;
        const delay = Math.min(
          2000 * Math.pow(2, reconnectCount.current),
          30000
        );
        setTimeout(connect, delay);
      }
    };

    es.onopen = () => {
      reconnectCount.current = 0;
    };
  }, [roomId, updateRoomStatus, updateExpertState, addLine, updateInsights]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  return { connect, disconnect };
}
