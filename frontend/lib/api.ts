import type { ChatRequest, ChatResponse } from "@/types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function sendChatMessage(message: string): Promise<string> {
  const body: ChatRequest = { message };

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
