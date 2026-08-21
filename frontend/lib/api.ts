import type { ChatRequest, ChatResponse, ChatStreamEvent } from "@/types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** Non-streaming fallback: send one message, wait for the complete reply. */
export async function sendChatMessage(
  message: string,
  threadId: string
): Promise<string> {
  const body: ChatRequest = { message, thread_id: threadId };

  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`Backend responded with status ${res.status}`);
  }

  const data: ChatResponse = await res.json();
  return data.response;
}

/**
 * Streams the assistant reply token-by-token from POST /api/chat/stream.
 *
 * Calls `onToken` for every incremental chunk so the UI can render text as
 * it arrives. Resolves with the final full reply once the "done" event is
 * received; rejects on HTTP or stream "error" events.
 *
 * Implemented with fetch + ReadableStream (manual SSE parsing) instead of
 * the native EventSource API because EventSource only supports GET requests,
 * while we need to POST the chat message body.
 */
export async function streamChatMessage(
  message: string,
  threadId: string,
  onToken: (text: string) => void
): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId } satisfies ChatRequest),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Backend responded with status ${res.status}`);
  }

  const reader = res.body.getReader();
  // TextDecoder with stream:true handles multi-byte characters split across chunks.
  const decoder = new TextDecoder();
  let buffer = "";
  let received = "";

  // SSE frames are separated by a blank line ("\n\n"); network chunks can
  // contain partial frames, so we keep a buffer and consume whole frames only.
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const event = parseSseFrame(frame);
      if (event) {
        switch (event.type) {
          case "token":
            received += event.content;
            onToken(event.content);
            break;
          case "done":
            return event.response;
          case "error":
            throw new Error(event.message);
        }
      }
      boundary = buffer.indexOf("\n\n");
    }
  }

  // Stream closed without a "done" frame (e.g. dropped connection):
  // fall back to whatever tokens already arrived.
  if (received.length > 0) return received;
  throw new Error("Stream ended unexpectedly before any response was received.");
}

/** Parse one `data: <json>` SSE frame into a typed ChatStreamEvent. */
function parseSseFrame(frame: string): ChatStreamEvent | null {
  const line = frame.split("\n").find((l) => l.startsWith("data: "));
  if (!line) return null;

  try {
    return JSON.parse(line.slice("data: ".length)) as ChatStreamEvent;
  } catch {
    // Ignore malformed frames instead of failing the whole stream.
    return null;
  }
}
