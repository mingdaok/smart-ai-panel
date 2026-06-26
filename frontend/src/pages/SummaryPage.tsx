import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoomDetail } from '../api/rooms';
import { useRoomStore } from '../store/roomSlice';
import SummaryPanel from '../components/summary/SummaryPanel';

export default function SummaryPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentRoom, setCurrentRoom } = useRoomStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    // If we already have room data from Store (navigated from Studio), skip refetch
    if (currentRoom && currentRoom.id === id) {
      setLoading(false);
      return;
    }
    // Cold load — direct page refresh or deep link
    getRoomDetail(id)
      .then((room) => {
        setCurrentRoom(room);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id, currentRoom, setCurrentRoom]);

  if (loading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{
          backgroundColor: 'var(--bg-primary)',
          color: 'var(--text-primary)',
        }}
      >
        加载中...
      </div>
    );
  }

  if (!currentRoom) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{
          backgroundColor: 'var(--bg-primary)',
          color: 'var(--text-primary)',
        }}
      >
        讨论未找到
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
      <button
        onClick={() => navigate('/')}
        className="mb-6 text-sm hover:underline"
        style={{ color: 'var(--text-secondary)' }}
      >
        ← 返回首页
      </button>
      <h1 className="text-2xl font-bold mb-2">讨论总结</h1>
      <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
        话题：{currentRoom.topic} | 状态：{currentRoom.status}
      </p>
      <SummaryPanel roomId={id!} />
    </div>
  );
}
