import { create } from 'zustand';

interface TranscriptLine {
  id: string;
  expert_id: string;
  name: string;
  title: string;
  color: string;
  content: string;
  line_type: string;
  sequence_num: number;
  created_at: string;
}

interface TranscriptState {
  lines: TranscriptLine[];
  isStreaming: boolean;
  setLines: (lines: TranscriptLine[]) => void;
  addLine: (line: TranscriptLine) => void;
}

export const useTranscriptStore = create<TranscriptState>((set) => ({
  lines: [],
  isStreaming: false,
  setLines: (lines) => set({ lines }),
  addLine: (line) =>
    set((state) => ({
      lines: [...state.lines, line],
    })),
}));
