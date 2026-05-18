import { getToken } from "@/lib/auth";
import type { BoardData } from "@/lib/kanban";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type AIResponse = {
  message: string;
  board_update: BoardData | null;
};

export async function sendMessage(
  history: ChatMessage[],
  userMessage: string
): Promise<AIResponse> {
  const token = getToken();
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ history, user_message: userMessage }),
  });
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);
  return res.json();
}
