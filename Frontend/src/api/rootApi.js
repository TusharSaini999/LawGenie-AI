import axios from "axios";
import config from "../config/config";

const api = axios.create({
  baseURL: config.api.baseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

// Chat
export const chatApi = async ({ query, token }) => {
  const requestConfig = {
    params: { q: query },
  };

  if (token) {
    requestConfig.headers = {
      Authorization: `Bearer ${token}`,
    };
  }

  const res = await api.get("/chat/", requestConfig);
  return res.data;
};

export const chatHistoryApi = async ({ token }) => {
  const requestConfig = {};

  if (token) {
    requestConfig.headers = {
      Authorization: `Bearer ${token}`,
    };
  }

  const res = await api.get("/chat/history", requestConfig);
  return res.data;
};
