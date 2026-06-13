import { create } from "zustand";

export interface VolunteerItem {
  id: number;
  university_id: number;
  university_name: string;
  university_level: string;
  major_id: number;
  major_name: string;
  major_category: string;
  priority: number;
  note: string;
}

export interface Plan {
  id: number;
  name: string;
  province_id: number;
  score: number;
  rank: number;
  subject_group: string;
  items: VolunteerItem[];
}

interface PlanState {
  plans: Plan[];
  currentPlan: Plan | null;
  setPlans: (plans: Plan[]) => void;
  setCurrentPlan: (plan: Plan | null) => void;
  reorderItems: (itemIds: number[]) => void;
  removeItem: (itemId: number) => void;
}

export const usePlanStore = create<PlanState>((set) => ({
  plans: [],
  currentPlan: null,
  setPlans: (plans) => set({ plans }),
  setCurrentPlan: (plan) => set({ currentPlan: plan }),
  reorderItems: (itemIds) =>
    set((state) => {
      if (!state.currentPlan) return state;
      const items = [...state.currentPlan.items];
      itemIds.forEach((id, idx) => {
        const item = items.find((i) => i.id === id);
        if (item) item.priority = idx + 1;
      });
      items.sort((a, b) => a.priority - b.priority);
      return { currentPlan: { ...state.currentPlan, items } };
    }),
  removeItem: (itemId) =>
    set((state) => {
      if (!state.currentPlan) return state;
      const items = state.currentPlan.items
        .filter((i) => i.id !== itemId)
        .map((item, idx) => ({ ...item, priority: idx + 1 }));
      return { currentPlan: { ...state.currentPlan, items } };
    }),
}));
