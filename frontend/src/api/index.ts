const BASE = "/api";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  // Provinces
  getProvinces: () => request<{ id: number; name: string; gaokao_mode: string }[]>("/provinces"),

  // Universities
  getUniversities: (params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<any>(`/universities?${qs}`);
  },

  // Majors
  getMajors: (params?: Record<string, string>) => {
    const qs = params ? new URLSearchParams(params).toString() : "";
    return request<any>(`/majors?${qs}`);
  },
  getCategories: () => request<string[]>("/majors/categories"),

  // Scores
  getScores: (params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<any>(`/scores?${qs}`);
  },
  getScoreHistory: (university_id: number, major_id: number, province_id: number) =>
    request<any>(`/scores/history?university_id=${university_id}&major_id=${major_id}&province_id=${province_id}`),

  // Recommend
  getRecommend: (params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<any>(`/recommend?${qs}`);
  },

  // Plans
  getPlans: () => request<any[]>("/plans"),
  getPlan: (id: number) => request<any>(`/plans/${id}`),
  createPlan: (params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<any>(`/plans?${qs}`, { method: "POST" });
  },
  updatePlan: (id: number, name: string) =>
    request<any>(`/plans/${id}?name=${encodeURIComponent(name)}`, { method: "PUT" }),
  deletePlan: (id: number) => request<any>(`/plans/${id}`, { method: "DELETE" }),
  addPlanItem: (planId: number, params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<any>(`/plans/${planId}/items?${qs}`, { method: "POST" });
  },
  deletePlanItem: (planId: number, itemId: number) =>
    request<any>(`/plans/${planId}/items/${itemId}`, { method: "DELETE" }),
  reorderItems: (planId: number, itemIds: number[]) =>
    request<any>(`/plans/${planId}/items/reorder?item_ids=${itemIds.join(",")}`, { method: "PUT" }),
};
