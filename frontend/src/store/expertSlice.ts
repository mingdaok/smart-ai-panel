import { create } from 'zustand';

type ExpertStatus = 'idle' | 'preparing' | 'speaking';

interface Expert {
  id: string;
  name: string;
  title: string;
  stance: string;
  color: string;
  role: 'host' | 'expert';
  position: number;
  current_status: ExpertStatus;
  public_thought: string;
}

interface ExpertState {
  experts: Expert[];
  host: Expert | null;
  setExperts: (host: Expert, experts: Expert[]) => void;
  updateExpertState: (
    expertId: string,
    status: ExpertStatus,
    thought: string
  ) => void;
}

export const useExpertStore = create<ExpertState>((set) => ({
  experts: [],
  host: null,
  setExperts: (host, experts) => set({ host, experts }),
  updateExpertState: (expertId, status, thought) =>
    set((state) => ({
      experts: state.experts.map((e) =>
        e.id === expertId
          ? { ...e, current_status: status, public_thought: thought }
          : e
      ),
      host:
        state.host?.id === expertId
          ? { ...state.host, current_status: status, public_thought: thought }
          : state.host,
    })),
}));
