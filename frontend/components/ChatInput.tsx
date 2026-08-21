"use client";

import { FormEvent, useState } from "react";

interface ChatInputProps {
  disabled: boolean;
  onSend: (message: string) => void;
}

export default function ChatInput({ disabled, onSend }: ChatInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 border-t border-zinc-200 p-4 dark:border-zinc-800">
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
        aria-label="Chat message"
        className="flex-1 rounded-full border border-zinc-300 bg-transparent px-4 py-2.5 text-sm outline-none focus:border-blue-500 disabled:opacity-50 dark:border-zinc-700"
      />
      <button
        type="submit"
        disabled={disabled || value.trim().length === 0}
        className="rounded-full bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Send
      </button>
    </form>
  );
}
