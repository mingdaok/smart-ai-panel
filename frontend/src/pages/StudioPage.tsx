import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoomDetail } from '../api/rooms';
import { useRoomStore } from '../store/roomSlice';
import { useExpertStore } from '../store/expertSlice';
import { useTranscriptStore } from '../store/transcriptSlice';
import { useInsightStore } from '../store/insightSlice';
import { useSSE } from '../hooks/useSSE';
import TranscriptPanel from '../components/studio/TranscriptPanel';
import ExpertPanel from '../components/studio/ExpertPanel';
import InsightPanel from '../components/studio/InsightPanel';
import ControlBar from '../components/studio/ControlBar';

export default function StudioPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setCurrentRoom, currentRoom } = useRoomStore();
  const { setExperts } = useExpertStore();
  const { setLines } = useTranscriptStore();
  const { setInsights } = useInsightStore();
  const { connect } = useSSE(id || null);

  useEffect(() => {
    if (!id) return;
    getRoomDetail(id)
      .then((room) => {
        setCurrentRoom(room);
        const hostExpert = room.experts.find((e) => e.role === 'host');
        const panelists = room.experts.filter((e) => e.role === 'expert');
        if (hostExpert) setExperts(hostExpert, panelists);
        setLines([]);
        setInsights([], []);
      })
      .catch(console.error);
  }, [id, setCurrentRoom, setExperts, setLines, setInsights]);

  useEffect(() => {
    if (
      currentRoom?.status === 'ready' ||
      currentRoom?.status === 'discussing'
    ) {
      connect();
    }
    if (
      currentRoom?.status === 'finished' ||
      currentRoom?.status === 'stopped'
    ) {
      navigate(`/room/${id}/summary`);
    }
  }, [currentRoom?.status, connect, id, navigate]);

  return (
    <div
      className="h-screen overflow-hidden flex flex-col"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
      }}
    >
      <ControlBar roomId={id || ''} />
      <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-3 xl:grid-cols-4 gap-0">
        {/* Transcript: main area, spans 2 cols on desktop/wide */}
        <div className="md:col-span-2 xl:col-span-2 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-hidden">
            <TranscriptPanel />
          </div>
        </div>
        {/* Expert panel: always visible on desktop+ */}
        <div className="overflow-hidden">
          <ExpertPanel />
        </div>
        {/* Insight panel: 4th column on wide, bottom panel on narrow/desktop */}
        <div className="hidden xl:block overflow-hidden">
          <InsightPanel />
        </div>
        <div
          className="xl:hidden overflow-hidden"
          style={{ maxHeight: '30vh' }}
        >
          <InsightPanel />
        </div>
      </div>
    </div>
  );
}
