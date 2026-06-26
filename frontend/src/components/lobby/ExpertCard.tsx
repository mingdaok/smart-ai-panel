import type { ExpertResponse } from '../../api/rooms';

export default function ExpertCard({
  expert,
  isHost = false,
}: {
  expert: ExpertResponse;
  isHost?: boolean;
}) {
  return (
    <div
      className="p-4 rounded-xl border"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: isHost ? '#94a3b8' : expert.color,
        borderLeftWidth: '4px',
      }}
    >
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold"
          style={{
            background: isHost
              ? 'linear-gradient(135deg, #f8fafc, #94a3b8)'
              : `linear-gradient(135deg, ${expert.color}, ${expert.color}88)`,
            color: isHost ? 'var(--host-text)' : '#fff',
          }}
        >
          {expert.name[0]}
        </div>
        <div>
          <h3 className="font-semibold">{expert.name}</h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {expert.title}
          </p>
        </div>
        {isHost && (
          <span
            className="ml-auto text-xs px-2 py-0.5 rounded"
            style={{ backgroundColor: 'var(--bg-card-hover)' }}
          >
            MC
          </span>
        )}
      </div>
      <p
        className="mt-3 text-sm italic"
        style={{ color: 'var(--text-secondary)' }}
      >
        「{expert.stance}」
      </p>
    </div>
  );
}
