import { useEffect, useState } from 'react';
import { getRoomDetail, type ExpertResponse } from '../../api/rooms';
import { useTranscriptStore } from '../../store/transcriptSlice';
import { useInsightStore } from '../../store/insightSlice';

export default function SummaryPanel({ roomId }: { roomId: string }) {
  const [transcriptCount, setTranscriptCount] = useState(0);
  const [insightCount, setInsightCount] = useState(0);

  useEffect(() => {
    getRoomDetail(roomId)
      .then((room) => {
        setTranscriptCount(room.transcript_count);
        setInsightCount(room.insight_count);
      })
      .catch(console.error);
  }, [roomId]);

  const lines = useTranscriptStore((s) => s.lines);
  const consensus = useInsightStore((s) => s.consensus);
  const disagreement = useInsightStore((s) => s.disagreement);

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div
          className="p-4 rounded-xl text-center"
          style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <p className="text-2xl font-bold">{transcriptCount}</p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            发言总数
          </p>
        </div>
        <div
          className="p-4 rounded-xl text-center"
          style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <p className="text-2xl font-bold" style={{ color: 'var(--color-consensus)' }}>
            {consensus.length}
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            共识观点
          </p>
        </div>
        <div
          className="p-4 rounded-xl text-center"
          style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <p className="text-2xl font-bold" style={{ color: 'var(--color-disagreement)' }}>
            {disagreement.length}
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            分歧观点
          </p>
        </div>
        <div
          className="p-4 rounded-xl text-center"
          style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <p className="text-2xl font-bold">{insightCount}</p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            洞察总数
          </p>
        </div>
      </div>

      {/* Consensus */}
      <div
        className="p-4 rounded-xl"
        style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-default)',
        }}
      >
        <h2
          className="text-lg font-semibold mb-3"
          style={{ color: 'var(--color-consensus)' }}
        >
          共识观点
        </h2>
        {consensus.length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            本次讨论中未提炼出明确共识
          </p>
        ) : (
          <ul className="space-y-2">
            {consensus.map((item) => (
              <li
                key={item.id}
                className="p-3 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--color-consensus-bg)' }}
              >
                {item.content}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Disagreement */}
      <div
        className="p-4 rounded-xl"
        style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-default)',
        }}
      >
        <h2
          className="text-lg font-semibold mb-3"
          style={{ color: 'var(--color-disagreement)' }}
        >
          分歧观点
        </h2>
        {disagreement.length === 0 ? (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            本次讨论中未出现明显分歧
          </p>
        ) : (
          <ul className="space-y-2">
            {disagreement.map((item) => (
              <li
                key={item.id}
                className="p-3 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--color-disagreement-bg)' }}
              >
                {item.content}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Transcript preview */}
      {lines.length > 0 && (
        <div
          className="p-4 rounded-xl"
          style={{
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
          }}
        >
          <h2 className="text-lg font-semibold mb-3">完整发言记录</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {lines.map((line) => (
              <div key={line.id} className="p-2 rounded-lg text-sm" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <span className="font-semibold" style={{ color: line.color }}>
                  {line.name}
                </span>
                ：{line.content}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
