import { create } from 'zustand';

interface Room {
  id: string;
  topic: string;
  expert_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

interface Expert {
  id: string;
  name: string;
  title: string;
  stance: string;
  color: string;
  role: 'host' | 'expert';
  position: number;
  current_status: 'idle' | 'preparing' | 'speaking';
  public_thought: string;
}

interface RoomDetail extends Room {
  experts: Expert[];
  transcript_count: number;
  insight_count: number;
}

interface RoomState {
  rooms: Room[];
  currentRoom: RoomDetail | null;
  setRooms: (rooms: Room[]) => void;
  setCurrentRoom: (room: RoomDetail) => void;
  updateRoomStatus: (id: string, status: string) => void;
}

export const useRoomStore = create<RoomState>((set) => ({
  rooms: [],
  currentRoom: null,
  setRooms: (rooms) => set({ rooms }),
  setCurrentRoom: (room) => set({ currentRoom: room }),
  updateRoomStatus: (id, status) =>
    set((state) => ({
      rooms: state.rooms.map((r) => (r.id === id ? { ...r, status } : r)),
      currentRoom:
        state.currentRoom?.id === id
          ? { ...state.currentRoom, status }
          : state.currentRoom,
    })),
}));
