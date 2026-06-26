import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startDiscussion, stopDiscussion } from '../../api/discussion';

export default function ControlBar({ roomId }: { roomId: string }) {
  const navigate = useNavigate();
  const [started, setStarted] = useState(false);
  const [stopping, setStopping] = useState(false);

  const handleStart = async () => {
    await startDiscussion(roomId);
    setStarted(true);
  };

  const handleStop = async () => {
    await stopDiscussion(roomId);
    setStopping(true);
  };

  return (
    <div
      className="flex items-center justify-between px-4 py-2 border-b flex-shrink-0"
      style={{
        backgroundColor: 'var(--bg-secondary)',
        borderColor: 'var(--border-default)',
      }}
    >
      <button
        onClick={() => navigate('/')}
        className="text-sm hover:underline"
        style={{ color: 'var(--text-secondary)' }}
      >
        ← 返回首页
      </button>
      <div className="flex gap-3">
        {!started && (
          <button
            onClick={handleStart}
            className="px-6 py-1.5 rounded-lg text-white text-sm font-medium"
            style={{
              background: 'linear-gradient(135deg, #10b981, #14b8a6)',
            }}
          >
            开始讨论
          </button>
        )}
        {started && !stopping && (
          <button
            onClick={handleStop}
            className="px-6 py-1.5 rounded-lg text-white text-sm font-medium"
            style={{
              background: 'linear-gradient(135deg, #ef4444, #dc2626)',
            }}
          >
            终止讨论
          </button>
        )}
      </div>
    </div>
  );
}
