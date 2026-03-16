import axios from "axios";
import config from "../config/config";

const api = axios.create({
  baseURL: config.api.baseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

// Chat
export const chatApi = async (data) => {
  const res = await api.post("/chat/", data);
  return res.data;
};
