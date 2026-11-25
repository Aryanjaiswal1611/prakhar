import { api, API_TIMEOUT_MS } from "./client";
import type { ChaosExperiment, SimulationResult, Remediation, WebsiteTestResult } from "../types";

export const chaosApi = {
  predefined: async () => (await api.get("/api/chaos/experiments/predefined")).data,
  custom: async () => (await api.get("/api/chaos/custom")).data,
  createCustom: async (payload:any) => (await api.post("/api/chaos/custom", payload)).data,
  simulate: async (payload:{infrastructure_id?:number; url?:string; experiment: ChaosExperiment; custom?:boolean; name?:string; description?:string}) =>
    (await api.post<SimulationResult>("/api/chaos/simulate", payload, { timeout: API_TIMEOUT_MS })).data,
};
export const remediationApi = {
  generate: async (payload:{run_id?:number; website_test_id?:number; url?:string; language:string}) => (await api.post<Remediation>("/api/remediation/generate", payload, { timeout: API_TIMEOUT_MS })).data,
  byRun: async (run_id:number) => (await api.get<Remediation[]>(`/api/remediation/run/${run_id}`, { timeout: API_TIMEOUT_MS })).data,
  byWebsiteTest: async (id:number) => (await api.get<Remediation[]>(`/api/remediation/website-test/${id}`, { timeout: API_TIMEOUT_MS })).data,
  validate: async (id:number) => (await api.post<Remediation>(`/api/remediation/${id}/validate`, {}, { timeout: API_TIMEOUT_MS })).data,
  approve: async (id:number) => (await api.post<Remediation>(`/api/remediation/${id}/approve`, {}, { timeout: API_TIMEOUT_MS })).data,
};
export const historyApi = {
  runs: async () => (await api.get("/api/history/runs", { timeout: API_TIMEOUT_MS })).data,
  run: async (id:number) => (await api.get(`/api/history/runs/${id}`, { timeout: API_TIMEOUT_MS })).data,
};
export const monitoringApi = {
  status: async () => (await api.get("/api/monitoring/status", { timeout: API_TIMEOUT_MS })).data,
  settings: async () => (await api.get("/api/monitoring/settings", { timeout: API_TIMEOUT_MS })).data,
  updateSettings: async (p:any) => (await api.put("/api/monitoring/settings", p, { timeout: API_TIMEOUT_MS })).data,
};
export const websiteTestApi = {
  run: async (payload:{url:string; mode:string; include_api_endpoint?:string}) => (await api.post<WebsiteTestResult>("/api/website-tests/run", payload, { timeout: API_TIMEOUT_MS })).data,
  list: async () => (await api.get("/api/website-tests", { timeout: API_TIMEOUT_MS })).data,
  get: async (id:number) => (await api.get<WebsiteTestResult>(`/api/website-tests/${id}`, { timeout: API_TIMEOUT_MS })).data,
};
export const discoveryApi = {
  infrastructure: async (url:string) => (await api.get("/api/discovery/infrastructure", { params:{url}, timeout: API_TIMEOUT_MS })).data,
};
export const chatbotApi = {
  ask: async (message:string, context?:any) => (await api.post("/api/chatbot/ask", {message, context}, { timeout: API_TIMEOUT_MS })).data,
};
