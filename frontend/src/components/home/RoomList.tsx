import type { RoomResponse } from '../../api/rooms';

const STATUS_LABELS: Record<string, string> = {
  waiting: '等待中',
  generating: '生成专家中',
  ready: '就绪',
  discussing: '讨论中',
  finished: '已结束',
  stopped: '已终止',
};

const STATUS_COLORS: Record<string, string> = {
  waiting: '#a0a0b0',
  generating: '#f59e0b',
  ready: '#10b981',
  discussing: '#6366f1',
  finished: '#6b7280',
  stopped: '#ef4444',
};

export default function RoomList({
  rooms,
  onEnter,
}: {
  rooms: RoomResponse[];
  onEnter: (id: string) => void;
}) {
  if (rooms.length === 0) {
    return (
      <div
        className="text-center py-12 rounded-xl border"
        style={{
          borderColor: 'var(--border-default)',
          backgroundColor: 'var(--bg-secondary)',
        }}
      >
        <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
          暂无讨论房间
        </p>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
          点击「+ 新建讨论」创建第一个圆桌讨论
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {rooms.map((room) => (
        <div
          key={room.id}
          onClick={() => onEnter(room.id)}
          className="p-4 rounded-xl border cursor-pointer transition-all duration-200 hover:border-[var(--border-active)]"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-default)',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.backgroundColor =
              'var(--bg-card-hover)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.backgroundColor =
              'var(--bg-card)';
          }}
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-lg">{room.topic}</h3>
              <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                {room.expert_count} 位专家
              </p>
            </div>
            <span
              className="text-xs px-2 py-1 rounded-full font-medium"
              style={{
                color: STATUS_COLORS[room.status] || '#a0a0b0',
                backgroundColor: `${STATUS_COLORS[room.status] || '#a0a0b0'}15`,
              }}
            >
              {STATUS_LABELS[room.status] || room.status}
            </span>
          </div>
          <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
            创建于 {new Date(room.created_at).toLocaleString('zh-CN')}
          </p>
        </div>
      ))}
    </div>
  );
}
