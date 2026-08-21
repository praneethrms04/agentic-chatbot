export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
}

/** Wire format expected by the FastAPI backend (snake_case fields). */
export interface ChatRequest {
  message: string;
  /** Conversation thread used by the backend for persistence. */
  thread_id: string;
}

export interface ChatResponse {
  response: string;
}

/**
 * Server-Sent Event payloads emitted by POST /api/chat/stream.
 * Mirrors backend app/schemas/chat.py:
 *   TokenEvent* -> (DoneEvent | ErrorEvent)
 */
export type ChatStreamEvent =
  | { type: "token"; content: string }
  | { type: "done"; response: string }
  | { type: "error"; message: string };
