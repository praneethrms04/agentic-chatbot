"use client";

import { useEffect, useRef, useState } from "react";

import { sendChatMessage } from "@/lib/api";
import type { ChatMessage } from "@/types/chat";
import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";

function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return { id: crypto.randomUUID(), role, content };
}

const WELCOME_MESSAGE = createMessage(
  "assistant",
  "Hi! I'm your AI assistant. How can I help you today?"
);

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend(text: string) {
    setMessages((prev) => [...prev, createMessage("user", text)]);
    setIsLoading(true);
    setError(null);

    try {
      const reply = await sendChatMessage(text);
      setMessages((prev) => [...prev, createMessage("assistant", reply)]);
    } catch {
      setError("Failed to get a response. Is the backend running?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex h-dvh w-full flex-col bg-white dark:bg-black">
      <header className="border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
        <h1 className="text-lg font-semibold">Agentic Chatbot</h1>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Powered by FastAPI + LangGraph + Gemini
        </p>
      </header>

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-3 overflow-y-auto p-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-zinc-100 px-4 py-2.5 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
              Thinking...
            </div>
          </div>
        )}

        {error && (
          <div className="flex justify-center">
            <p className="rounded-full bg-red-50 px-4 py-1.5 text-xs text-red-600 dark:bg-red-950/50 dark:text-red-400">
              {error}
            </p>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <div className="mx-auto w-full max-w-3xl">
        <ChatInput disabled={isLoading} onSend={handleSend} />
      </div>
    </div>
  );
}
