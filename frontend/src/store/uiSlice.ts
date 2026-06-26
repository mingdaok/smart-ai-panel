import { create } from 'zustand';

type Breakpoint = 'narrow' | 'desktop' | 'wide';

interface UIState {
  sidebarCollapsed: boolean;
  activeBreakpoint: Breakpoint;
  toggleSidebar: () => void;
  setBreakpoint: (bp: Breakpoint) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  activeBreakpoint: 'desktop',
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setBreakpoint: (bp) => set({ activeBreakpoint: bp }),
}));
