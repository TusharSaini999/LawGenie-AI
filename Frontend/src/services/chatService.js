import { chatApi, chatHistoryApi } from "@/api/rootApi";
import { SERVER_ERROR_MSG } from "@/constants/Messages";

const CHAT_TOKEN_STORAGE_KEY = "lawgenie_chat_token";

class ChatService {
  constructor() {}

  getToken() {
    try {
      return localStorage.getItem(CHAT_TOKEN_STORAGE_KEY) || "";
    } catch {
      return "";
    }
  }

  saveToken(token) {
    if (!token) return;

    try {
      localStorage.setItem(CHAT_TOKEN_STORAGE_KEY, token);
    } catch {
      // Ignore storage failures in restricted environments.
    }
  }

  clearToken() {
    try {
      localStorage.removeItem(CHAT_TOKEN_STORAGE_KEY);
    } catch {
      // Ignore storage failures in restricted environments.
    }
  }

  startNewChat() {
    this.clearToken();
  }

  extractErrorMessage(error) {
    const backendDetail = error?.response?.data?.detail;
    if (typeof backendDetail === "string" && backendDetail.trim()) {
      return backendDetail.trim();
    }

    const backendMessage = error?.response?.data?.message;
    if (typeof backendMessage === "string" && backendMessage.trim()) {
      return backendMessage.trim();
    }

    if (typeof error?.message === "string" && error.message.trim()) {
      return error.message.trim();
    }

    return SERVER_ERROR_MSG;
  }

  extractReply(payload) {
    if (!payload) return "";

    if (typeof payload === "string") {
      const text = payload.trim();
      if (text.toLowerCase().startsWith("<!doctype html")) {
        throw new Error(
          "Chat API returned HTML instead of JSON. Check VITE_API_BASE_URL backend URL.",
        );
      }

      return text;
    }

    const nestedResponse = payload.response;
    if (nestedResponse && typeof nestedResponse === "object") {
      const nestedText =
        nestedResponse.answer || nestedResponse.message || nestedResponse.response;

      if (typeof nestedText === "string") return nestedText.trim();
    }

    return (
      payload.answer ||
      payload.response ||
      payload.message ||
      payload.data?.answer ||
      payload.data?.message ||
      ""
    )
      .toString()
      .trim();
  }

  async sendMessage({ message }) {
    const payload = {
      query: message,
      token: this.getToken(),
    };

    try {
      const response = await chatApi(payload);

      if (typeof response === "string") {
        const htmlLike = response.trim().toLowerCase().startsWith("<!doctype html");
        if (htmlLike) {
          throw new Error(
            "Chat API returned HTML instead of JSON. Check VITE_API_BASE_URL backend URL.",
          );
        }
      }

      this.saveToken(response?.token);
      const reply = this.extractReply(response);

      if (!reply) {
        throw new Error(SERVER_ERROR_MSG);
      }

      return {
        reply,
        tokenStatus: response?.token_status || "",
      };
    } catch (error) {
      throw new Error(this.extractErrorMessage(error));
    }
  }

  normalizeRole(role) {
    const normalized = (role || "").toString().trim().toLowerCase();

    if (normalized === "assistant" || normalized === "ai response") {
      return "assistant";
    }

    return "user";
  }

  parseHistoryItem(item = {}) {
    const createdAt = item?.timestamp ? new Date(item.timestamp) : new Date();

    return {
      role: this.normalizeRole(item?.role),
      text: (item?.message || "").toString(),
      createdAt: Number.isNaN(createdAt.getTime()) ? new Date() : createdAt,
    };
  }

  async getHistory() {
    const token = this.getToken();

    if (!token) {
      return {
        hasHistory: false,
        history: [],
      };
    }

    try {
      const response = await chatHistoryApi({ token });

      const history = Array.isArray(response?.history)
        ? response.history
            .map((item) => this.parseHistoryItem(item))
            .filter((item) => item.text.trim().length > 0)
        : [];

      return {
        hasHistory: history.length > 0,
        history,
      };
    } catch (error) {
      if (error?.response?.status === 401) {
        this.clearToken();
      }

      throw new Error(this.extractErrorMessage(error));
    }
  }
}

const chatService = new ChatService();
export default chatService;
