import { create } from 'zustand';

interface InsightItem {
  id: string;
  type: 'consensus' | 'disagreement';
  content: string;
}

interface InsightState {
  consensus: InsightItem[];
  disagreement: InsightItem[];
  setInsights: (consensus: InsightItem[], disagreement: InsightItem[]) => void;
  updateInsights: (
    consensus: InsightItem[],
    disagreement: InsightItem[]
  ) => void;
}

export const useInsightStore = create<InsightState>((set) => ({
  consensus: [],
  disagreement: [],
  setInsights: (consensus, disagreement) => set({ consensus, disagreement }),
  updateInsights: (consensus, disagreement) =>
    set({ consensus, disagreement }),
}));
