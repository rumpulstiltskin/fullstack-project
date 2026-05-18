import { clearToken, getToken } from "@/lib/auth";
import type { BoardData } from "@/lib/kanban";

function authHeaders(): HeadersInit {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function checkStatus(res: Response): void {
  if (res.status === 401) {
    clearToken();
    throw new Error("401");
  }
  if (!res.ok) throw new Error(String(res.status));
}

export async function getBoard(): Promise<BoardData> {
  const res = await fetch("/api/board", { headers: authHeaders() });
  checkStatus(res);
  return res.json();
}

export async function putBoard(board: BoardData): Promise<void> {
  const res = await fetch("/api/board", {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(board),
  });
  checkStatus(res);
}
