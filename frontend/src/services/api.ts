import { API_URLS } from "./urls";

export function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

export function setAccessToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearAccessToken(): void {
  localStorage.removeItem("access_token");
}

async function apiRequest<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getAccessToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `HTTP error ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function checkHealth<T>() {
  return apiRequest<T>(API_URLS.health);
}

export async function login<T>(credentials: {
  email: string;
  password: string;
}): Promise<T> {
  const data = await apiRequest<T>(API_URLS.auth.login, {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  const result = data as { access_token?: string };

  if (result.access_token) {
    setAccessToken(result.access_token);
  }

  return data;
}

export function register<T>(payload: {
  email: string;
  password: string;
}): Promise<T> {
  return apiRequest<T>(API_URLS.auth.register, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser<T>(): Promise<T> {
  return apiRequest<T>(API_URLS.auth.me);
}

export function logout(): void {
  clearAccessToken();
}

export function getDocuments<T>(): Promise<T> {
  return apiRequest<T>(API_URLS.documents.list);
}

export function getDocument<T>(documentId: string): Promise<T> {
  return apiRequest<T>(API_URLS.documents.detail(documentId));
}

export function uploadDocument<T>(file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest<T>(API_URLS.documents.upload, {
    method: "POST",
    body: formData,
  });
}

export function deleteDocument(documentId: string): Promise<void> {
  return apiRequest<void>(API_URLS.documents.delete(documentId), {
    method: "DELETE",
  });
}

export function getChats<T>(): Promise<T> {
  return apiRequest<T>(API_URLS.chats.list);
}

export function createChat<T>(payload: unknown = {}): Promise<T> {
  return apiRequest<T>(API_URLS.chats.create, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getChat<T>(chatId: string): Promise<T> {
  return apiRequest<T>(API_URLS.chats.detail(chatId));
}

export function deleteChat(chatId: string): Promise<void> {
  return apiRequest<void>(API_URLS.chats.delete(chatId), {
    method: "DELETE",
  });
}

export function askQuestion<T>(payload: unknown): Promise<T> {
  return apiRequest<T>(API_URLS.questions.ask, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
