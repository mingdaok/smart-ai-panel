export default function ExpertConfirmPanel({
  onConfirm,
  onBack,
}: {
  onConfirm: () => void;
  onBack: () => void;
}) {
  return (
    <div
      className="flex justify-between items-center p-4 rounded-xl"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      <div>
        <p className="text-sm font-medium">确认专家阵容后进入演播厅</p>
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          你仍然可以在讨论开始前取消或重新生成
        </p>
      </div>
      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="px-5 py-2 rounded-lg text-sm font-medium"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            color: 'var(--text-secondary)',
          }}
        >
          返回
        </button>
        <button
          onClick={onConfirm}
          className="px-5 py-2 rounded-lg text-white text-sm font-medium"
          style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          }}
        >
          确认进入演播厅
        </button>
      </div>
    </div>
  );
}
