import { api } from "./client";
import type { Infrastructure } from "../types";

export const graphApi = {
  list: async () => (await api.get<Infrastructure[]>("/api/graphs")).data,
  get: async (id:number) => (await api.get<Infrastructure>(`/api/graphs/${id}`)).data,
  create: async (payload: Omit<Infrastructure,"id">) => (await api.post<Infrastructure>("/api/graphs", payload)).data,
  update: async (id:number, payload: Omit<Infrastructure,"id">) => (await api.put<Infrastructure>(`/api/graphs/${id}`, payload)).data,
  remove: async (id:number) => (await api.delete(`/api/graphs/${id}`)).data,
  export: async (id:number) => (await api.get(`/api/graphs/${id}/export`)).data,
  import: async (payload: Omit<Infrastructure,"id">) => (await api.post<Infrastructure>("/api/graphs/import", payload)).data,
};
