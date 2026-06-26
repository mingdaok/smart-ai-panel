import { useEffect, useRef } from 'react';
import { useTranscriptStore } from '../../store/transcriptSlice';

const TYPE_LABELS: Record<string, string> = {
  opening: '开场',
  argument: '论点',
  rebuttal: '反驳',
  supplement: '补充',
  question: '提问',
  closing: '总结',
};

export default function TranscriptPanel() {
  const lines = useTranscriptStore((s) => s.lines);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [lines.length]);

  return (
    <div
      className="h-full overflow-y-auto p-4"
      style={{ backgroundColor: 'var(--bg-transcript)' }}
    >
      <h3
        className="text-sm font-semibold mb-3"
        style={{ color: 'var(--text-secondary)' }}
      >
        现场字幕
      </h3>
      {lines.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          讨论尚未开始，等待主持人开场...
        </p>
      )}
      <div className="space-y-3">
        {lines.map((line) => (
          <div key={line.id} className="flex gap-3">
            <div className="flex-shrink-0 mt-1">
              <span
                className="inline-block text-xs px-1.5 py-0.5 rounded font-medium"
                style={{
                  color: line.color,
                  backgroundColor: `${line.color}15`,
                }}
              >
                {TYPE_LABELS[line.line_type] || line.line_type}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span
                  className="font-semibold text-sm"
                  style={{ color: line.color }}
                >
                  {line.name}
                </span>
                <span
                  className="text-xs"
                  style={{ color: 'var(--text-muted)' }}
                >
                  {line.title}
                </span>
              </div>
              <p className="mt-1 text-sm leading-relaxed">{line.content}</p>
            </div>
          </div>
        ))}
      </div>
      <div ref={bottomRef} />
    </div>
  );
}
