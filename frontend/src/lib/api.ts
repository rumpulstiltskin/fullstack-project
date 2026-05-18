import { getToken } from "@/lib/auth";
import type { BoardData } from "@/lib/kanban";

function authHeaders(): HeadersInit {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getBoard(): Promise<BoardData> {
  const res = await fetch("/api/board", { headers: authHeaders() });
  if (!res.ok) throw new Error(`Failed to load board: ${res.status}`);
  return res.json();
}

export async function putBoard(board: BoardData): Promise<void> {
  const res = await fetch("/api/board", {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(board),
  });
  if (!res.ok) throw new Error(`Failed to save board: ${res.status}`);
}
