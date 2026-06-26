import { useInsightStore } from '../../store/insightSlice';

export default function InsightPanel() {
  const consensus = useInsightStore((s) => s.consensus);
  const disagreement = useInsightStore((s) => s.disagreement);

  return (
    <div
      className="h-full overflow-y-auto p-4"
      style={{ backgroundColor: 'var(--bg-secondary)' }}
    >
      <h3
        className="text-sm font-semibold mb-3"
        style={{ color: 'var(--text-secondary)' }}
      >
        实时洞察
      </h3>

      <div className="mb-4">
        <h4
          className="text-sm font-medium mb-2"
          style={{ color: 'var(--color-consensus)' }}
        >
          共识
        </h4>
        {consensus.length === 0 ? (
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            尚未提炼出共识...
          </p>
        ) : (
          <ul className="space-y-2">
            {consensus.map((item) => (
              <li
                key={item.id}
                className="p-2 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--color-consensus-bg)' }}
              >
                {item.content}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h4
          className="text-sm font-medium mb-2"
          style={{ color: 'var(--color-disagreement)' }}
        >
          分歧
        </h4>
        {disagreement.length === 0 ? (
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            尚未提炼出分歧...
          </p>
        ) : (
          <ul className="space-y-2">
            {disagreement.map((item) => (
              <li
                key={item.id}
                className="p-2 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--color-disagreement-bg)' }}
              >
                {item.content}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
