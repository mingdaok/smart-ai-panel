import { useState } from 'react';

export default function NewRoomDialog({
  onSubmit,
  onCancel,
}: {
  onSubmit: (topic: string, count: number) => void;
  onCancel: () => void;
}) {
  const [topic, setTopic] = useState('');
  const [count, setCount] = useState(4);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    const trimmed = topic.trim();
    if (!trimmed) {
      setError('请输入讨论话题');
      return;
    }
    if (trimmed.length > 200) {
      setError('话题名称不能超过 200 个字符');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await onSubmit(trimmed, count);
    } catch {
      setError('创建失败，请重试');
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0,0,0,0.6)' }}
      onClick={onCancel}
    >
      <div
        className="w-full max-w-md mx-4 p-6 rounded-2xl"
        style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-default)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-xl font-bold mb-4">新建讨论</h2>

        <label className="block mb-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          讨论话题
        </label>
        <input
          type="text"
          value={topic}
          onChange={(e) => { setTopic(e.target.value); setError(''); }}
          placeholder="输入讨论话题..."
          className="w-full px-3 py-2 rounded-lg mb-4 text-sm outline-none"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)',
          }}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(); }}
          autoFocus
        />

        <label className="block mb-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          专家人数: {count}
        </label>
        <input
          type="range"
          min={2}
          max={8}
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
          className="w-full mb-4 accent-[#6366f1]"
        />
        <div className="flex justify-between text-xs mb-6" style={{ color: 'var(--text-muted)' }}>
          <span>2 人</span>
          <span>8 人</span>
        </div>

        {error && (
          <p
            className="text-sm mb-4 px-3 py-2 rounded-lg"
            style={{ backgroundColor: 'rgba(239,68,68,0.1)', color: '#ef4444' }}
          >
            {error}
          </p>
        )}

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            disabled={submitting}
            className="px-4 py-2 rounded-lg text-sm"
            style={{
              backgroundColor: 'var(--bg-secondary)',
              color: 'var(--text-secondary)',
            }}
          >
            取消
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              opacity: submitting ? 0.6 : 1,
            }}
          >
            {submitting ? '创建中...' : '创建并进入'}
          </button>
        </div>
      </div>
    </div>
  );
}
