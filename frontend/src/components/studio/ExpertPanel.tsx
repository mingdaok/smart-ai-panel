import { useExpertStore } from '../../store/expertSlice';
import ExpertMiniCard from './ExpertMiniCard';

export default function ExpertPanel() {
  const host = useExpertStore((s) => s.host);
  const experts = useExpertStore((s) => s.experts);

  return (
    <div
      className="h-full overflow-y-auto p-4"
      style={{ backgroundColor: 'var(--bg-secondary)' }}
    >
      <h3
        className="text-sm font-semibold mb-3"
        style={{ color: 'var(--text-secondary)' }}
      >
        专家状态
      </h3>
      {host && (
        <div className="mb-3">
          <ExpertMiniCard expert={host} />
        </div>
      )}
      <div className="flex flex-col gap-2">
        {experts.map((expert) => (
          <ExpertMiniCard key={expert.id} expert={expert} />
        ))}
      </div>
    </div>
  );
}
