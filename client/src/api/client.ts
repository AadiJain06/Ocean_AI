import axios, { type AxiosRequestHeaders } from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers = (config.headers as AxiosRequestHeaders) || {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }
  if (config.url === "/projects") {
    config.url = "/projects/";
  }
  return config;
});

export default api;

