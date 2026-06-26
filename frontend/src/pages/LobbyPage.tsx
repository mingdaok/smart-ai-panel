import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoomDetail, generateExperts, type ExpertResponse } from '../api/rooms';
import { useExpertStore } from '../store/expertSlice';
import ExpertCard from '../components/lobby/ExpertCard';
import ExpertConfirmPanel from '../components/lobby/ExpertConfirmPanel';

export default function LobbyPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { experts, host, setExperts } = useExpertStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getRoomDetail(id)
      .then((room) => {
        const hostExpert = room.experts.find((e) => e.role === 'host');
        const panelists = room.experts.filter((e) => e.role === 'expert');
        if (hostExpert && panelists.length > 0) {
          setExperts(hostExpert, panelists);
          setLoading(false);
          return;
        }
        // Generate if no experts yet
        generateExperts(id)
          .then((data) => {
            setExperts(data.host, data.experts);
            setLoading(false);
          })
          .catch(() => setLoading(false));
      })
      .catch(() => setLoading(false));
  }, [id, setExperts]);

  const handleConfirm = () => {
    navigate(`/room/${id}/studio`);
  };

  if (loading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{
          backgroundColor: 'var(--bg-primary)',
          color: 'var(--text-primary)',
        }}
      >
        生成专家阵容中...
      </div>
    );
  }

  return (
    <div
      className="min-h-screen p-6"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
      }}
    >
      <h1 className="text-2xl font-bold mb-2">专家阵容确认</h1>
      <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
        请确认以下由 AI 生成的专家阵容，确认后将正式进入演播厅
      </p>
      {host && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3">主持人</h2>
          <ExpertCard expert={host} isHost />
        </div>
      )}
      <h2 className="text-lg font-semibold mb-3">
        讨论专家 ({experts.length}人)
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {experts.map((expert) => (
          <ExpertCard key={expert.id} expert={expert} />
        ))}
      </div>
      <ExpertConfirmPanel
        onConfirm={handleConfirm}
        onBack={() => navigate('/')}
      />
    </div>
  );
}
