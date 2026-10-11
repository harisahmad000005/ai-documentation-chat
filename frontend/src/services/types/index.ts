export interface User {
  id: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  status?: string;
  created_at?: string;
}

export interface Source {
  document_id: string;
  filename: string;
  page?: number | null;
  line_start?: number | null;
  line_end?: number | null;
  content?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;

  sources?: Source[];
}
