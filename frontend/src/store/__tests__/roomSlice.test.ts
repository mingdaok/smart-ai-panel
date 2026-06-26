import { describe, it, expect, beforeEach } from 'vitest';
import { useRoomStore } from '../roomSlice';
import { useExpertStore } from '../expertSlice';
import { useTranscriptStore } from '../transcriptSlice';
import { useInsightStore } from '../insightSlice';
import { useUIStore } from '../uiSlice';

// Helper to reset all stores between tests
function resetAllStores() {
  useRoomStore.setState({ rooms: [], currentRoom: null });
  useExpertStore.setState({ experts: [], host: null });
  useTranscriptStore.setState({ lines: [], isStreaming: false });
  useInsightStore.setState({ consensus: [], disagreement: [] });
  useUIStore.setState({ sidebarCollapsed: false, activeBreakpoint: 'desktop' });
}

describe('roomSlice', () => {
  beforeEach(() => resetAllStores());

  it('starts with empty rooms', () => {
    const { rooms } = useRoomStore.getState();
    expect(rooms).toEqual([]);
  });

  it('starts with null currentRoom', () => {
    const { currentRoom } = useRoomStore.getState();
    expect(currentRoom).toBeNull();
  });

  it('sets rooms', () => {
    const rooms = [
      { id: '1', topic: 'Test', expert_count: 4, status: 'waiting', created_at: 'now', updated_at: 'now' },
    ];
    useRoomStore.getState().setRooms(rooms);
    expect(useRoomStore.getState().rooms).toEqual(rooms);
  });

  it('sets currentRoom', () => {
    const room = {
      id: '1', topic: 'Test', expert_count: 4, status: 'waiting',
      created_at: 'now', updated_at: 'now', experts: [], transcript_count: 0, insight_count: 0,
    };
    useRoomStore.getState().setCurrentRoom(room);
    expect(useRoomStore.getState().currentRoom).toEqual(room);
  });

  it('updates room status in rooms list', () => {
    useRoomStore.getState().setRooms([
      { id: '1', topic: 'A', expert_count: 4, status: 'waiting', created_at: 'n', updated_at: 'n' },
      { id: '2', topic: 'B', expert_count: 3, status: 'waiting', created_at: 'n', updated_at: 'n' },
    ]);
    useRoomStore.getState().updateRoomStatus('1', 'discussing');
    const { rooms } = useRoomStore.getState();
    expect(rooms[0].status).toBe('discussing');
    expect(rooms[1].status).toBe('waiting');
  });

  it('updates currentRoom status when id matches', () => {
    const room = {
      id: '1', topic: 'Test', expert_count: 4, status: 'waiting',
      created_at: 'n', updated_at: 'n', experts: [], transcript_count: 0, insight_count: 0,
    };
    useRoomStore.getState().setCurrentRoom(room);
    useRoomStore.getState().updateRoomStatus('1', 'finished');
    expect(useRoomStore.getState().currentRoom?.status).toBe('finished');
  });
});

describe('expertSlice', () => {
  beforeEach(() => resetAllStores());

  const mockExpert = (overrides = {}) => ({
    id: 'e1', name: 'Test', title: 'Tester', stance: 'neutral',
    color: '#6366f1', role: 'expert' as const, position: 0,
    current_status: 'idle' as const, public_thought: '',
    ...overrides,
  });

  it('starts with empty experts and null host', () => {
    const { experts, host } = useExpertStore.getState();
    expect(experts).toEqual([]);
    expect(host).toBeNull();
  });

  it('sets host and experts', () => {
    const host = mockExpert({ id: 'h1', role: 'host', name: 'Host' });
    const expert = mockExpert({ id: 'e1', name: 'Expert1' });
    useExpertStore.getState().setExperts(host, [expert]);
    const state = useExpertStore.getState();
    expect(state.host?.id).toBe('h1');
    expect(state.experts).toHaveLength(1);
    expect(state.experts[0].id).toBe('e1');
  });

  it('updates expert state by id', () => {
    const host = mockExpert({ id: 'h1', role: 'host', name: 'Host' });
    const expert = mockExpert({ id: 'e1', name: 'Expert1' });
    useExpertStore.getState().setExperts(host, [expert]);

    useExpertStore.getState().updateExpertState('e1', 'speaking', 'thinking...');
    const state = useExpertStore.getState();
    expect(state.experts[0].current_status).toBe('speaking');
    expect(state.experts[0].public_thought).toBe('thinking...');
  });

  it('updates host state when id matches host', () => {
    const host = mockExpert({ id: 'h1', role: 'host', name: 'Host' });
    useExpertStore.getState().setExperts(host, []);
    useExpertStore.getState().updateExpertState('h1', 'speaking', 'host speaking');
    expect(useExpertStore.getState().host?.current_status).toBe('speaking');
  });
});

describe('transcriptSlice', () => {
  beforeEach(() => resetAllStores());

  const mockLine = (overrides = {}) => ({
    id: 't1', expert_id: 'e1', name: 'Expert', title: 'Tester',
    color: '#6366f1', content: 'Hello', line_type: 'argument',
    sequence_num: 1, created_at: 'now',
    ...overrides,
  });

  it('starts with empty lines and isStreaming false', () => {
    const { lines, isStreaming } = useTranscriptStore.getState();
    expect(lines).toEqual([]);
    expect(isStreaming).toBe(false);
  });

  it('sets lines', () => {
    const lines = [mockLine(), mockLine({ id: 't2', sequence_num: 2 })];
    useTranscriptStore.getState().setLines(lines);
    expect(useTranscriptStore.getState().lines).toHaveLength(2);
  });

  it('appends a line via addLine', () => {
    useTranscriptStore.getState().setLines([mockLine()]);
    useTranscriptStore.getState().addLine(mockLine({ id: 't2', sequence_num: 2, content: 'New' }));
    const lines = useTranscriptStore.getState().lines;
    expect(lines).toHaveLength(2);
    expect(lines[1].content).toBe('New');
  });
});

describe('insightSlice', () => {
  beforeEach(() => resetAllStores());

  const mockInsight = (overrides = {}) => ({
    id: 'i1', type: 'consensus' as const, content: 'Agreed on X',
    ...overrides,
  });

  it('starts with empty consensus and disagreement', () => {
    const { consensus, disagreement } = useInsightStore.getState();
    expect(consensus).toEqual([]);
    expect(disagreement).toEqual([]);
  });

  it('sets insights', () => {
    const c = [mockInsight({ id: 'c1', type: 'consensus' })];
    const d = [mockInsight({ id: 'd1', type: 'disagreement' })];
    useInsightStore.getState().setInsights(c, d);
    const state = useInsightStore.getState();
    expect(state.consensus).toHaveLength(1);
    expect(state.disagreement).toHaveLength(1);
  });

  it('updates insights', () => {
    useInsightStore.getState().setInsights([], []);
    const c = [mockInsight({ id: 'c1' })];
    const d = [mockInsight({ id: 'd1', type: 'disagreement' })];
    useInsightStore.getState().updateInsights(c, d);
    const state = useInsightStore.getState();
    expect(state.consensus).toHaveLength(1);
    expect(state.disagreement).toHaveLength(1);
  });
});

describe('uiSlice', () => {
  beforeEach(() => resetAllStores());

  it('starts with sidebarCollapsed false and activeBreakpoint desktop', () => {
    const { sidebarCollapsed, activeBreakpoint } = useUIStore.getState();
    expect(sidebarCollapsed).toBe(false);
    expect(activeBreakpoint).toBe('desktop');
  });

  it('toggles sidebar', () => {
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarCollapsed).toBe(true);
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarCollapsed).toBe(false);
  });

  it('sets breakpoint', () => {
    useUIStore.getState().setBreakpoint('wide');
    expect(useUIStore.getState().activeBreakpoint).toBe('wide');
    useUIStore.getState().setBreakpoint('narrow');
    expect(useUIStore.getState().activeBreakpoint).toBe('narrow');
  });
});
