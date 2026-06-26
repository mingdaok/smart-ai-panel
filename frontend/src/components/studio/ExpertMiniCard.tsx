import type { ExpertResponse } from '../../api/rooms';

const ANIMATION_MAP: Record<string, string> = {
  idle: 'var(--anim-idle)',
  preparing: 'var(--anim-preparing)',
  speaking: 'var(--anim-speaking)',
};

const STATUS_LABELS: Record<string, string> = {
  idle: '待机',
  preparing: '准备发言',
  speaking: '发言中',
};

export default function ExpertMiniCard({ expert }: { expert: ExpertResponse }) {
  const isHost = expert.role === 'host';
  const animation = ANIMATION_MAP[expert.current_status] || ANIMATION_MAP.idle;
  const statusLabel =
    STATUS_LABELS[expert.current_status] || expert.current_status;

  return (
    <div
      className="p-3 rounded-xl border transition-all duration-300"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor:
          expert.current_status === 'speaking'
            ? expert.color
            : 'var(--border-default)',
        animation,
      }}
    >
      <div className="flex items-center gap-2">
        <div
          className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold"
          style={{
            background: isHost
              ? 'var(--host-gradient)'
              : `var(--expert-gradient-${expert.position % 8})`,
            color: isHost ? 'var(--host-text)' : '#fff',
          }}
        >
          {expert.name[0]}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold truncate">{expert.name}</p>
          <p
            className="text-xs truncate"
            style={{ color: 'var(--text-muted)' }}
          >
            {expert.title}
          </p>
        </div>
        <span
          className="text-xs px-1.5 py-0.5 rounded"
          style={{
            backgroundColor:
              expert.current_status === 'speaking'
                ? `${expert.color}33`
                : 'transparent',
            color:
              expert.current_status === 'speaking'
                ? expert.color
                : 'var(--text-muted)',
          }}
        >
          {statusLabel}
        </span>
      </div>
      {expert.public_thought && (
        <p
          className="mt-2 text-xs italic"
          style={{ color: 'var(--text-secondary)' }}
        >
          {expert.public_thought}
        </p>
      )}
    </div>
  );
}
