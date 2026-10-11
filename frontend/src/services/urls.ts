const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const API_PREFIX = "/api/v1";

export const API_URLS = {
  health: `${API_BASE_URL}${API_PREFIX}/health`,

  auth: {
    login: `${API_BASE_URL}${API_PREFIX}/auth/login`,
    register: `${API_BASE_URL}${API_PREFIX}/auth/register`,
    refresh: `${API_BASE_URL}${API_PREFIX}/auth/refresh`,
    me: `${API_BASE_URL}${API_PREFIX}/auth/me`,
  },

  documents: {
    list: `${API_BASE_URL}${API_PREFIX}/documents`,
    detail: (documentId: string) =>
      `${API_BASE_URL}${API_PREFIX}/documents/${documentId}`,
    upload: `${API_BASE_URL}${API_PREFIX}/documents`,
    delete: (documentId: string) =>
      `${API_BASE_URL}${API_PREFIX}/documents/${documentId}`,
  },

  questions: {
    ask: `${API_BASE_URL}${API_PREFIX}/questions`,
  },

  chats: {
    list: `${API_BASE_URL}${API_PREFIX}/chats`,
    create: `${API_BASE_URL}${API_PREFIX}/chats`,
    detail: (chatId: string) => `${API_BASE_URL}${API_PREFIX}/chats/${chatId}`,
    delete: (chatId: string) => `${API_BASE_URL}${API_PREFIX}/chats/${chatId}`,
  },
} as const;
