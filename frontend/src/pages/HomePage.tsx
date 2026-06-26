import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listRooms, createRoom, type RoomResponse } from '../api/rooms';
import { useRoomStore } from '../store/roomSlice';
import RoomList from '../components/home/RoomList';
import NewRoomDialog from '../components/home/NewRoomDialog';

export default function HomePage() {
  const navigate = useNavigate();
  const { rooms, setRooms } = useRoomStore();
  const [showDialog, setShowDialog] = useState(false);

  useEffect(() => {
    listRooms()
      .then((data) => setRooms(data.rooms))
      .catch(console.error);
  }, [setRooms]);

  const handleCreate = async (topic: string, count: number) => {
    const room = await createRoom(topic, count);
    setShowDialog(false);
    navigate(`/room/${room.id}/lobby`);
  };

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
      }}
    >
      <header
        className="p-6 border-b"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <h1 className="text-2xl font-bold">AI Panel Studio</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          AI 圆桌讨论
        </p>
      </header>
      <main className="p-6">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-xl font-semibold">讨论列表</h2>
          <button
            onClick={() => setShowDialog(true)}
            className="px-4 py-2 rounded-lg text-white font-medium"
            style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            }}
          >
            + 新建讨论
          </button>
        </div>
        <RoomList
          rooms={rooms}
          onEnter={(id) => navigate(`/room/${id}/lobby`)}
        />
      </main>
      {showDialog && (
        <NewRoomDialog
          onSubmit={handleCreate}
          onCancel={() => setShowDialog(false)}
        />
      )}
    </div>
  );
}
