import axios from "axios";

export const API_TIMEOUT_MS = 45000;
const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const api = axios.create({ baseURL, timeout: API_TIMEOUT_MS });
