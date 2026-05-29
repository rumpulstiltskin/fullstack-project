import { clearLoggedIn } from "@/lib/auth";
import type { BoardData } from "@/lib/kanban";

function checkStatus(res: Response): void {
  if (res.status === 401) {
    clearLoggedIn();
    throw new Error("401");
  }
  if (!res.ok) throw new Error(String(res.status));
}

export async function getBoard(): Promise<BoardData> {
  const res = await fetch("/api/board", {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });
  checkStatus(res);
  return res.json() as Promise<BoardData>;
}

export async function putBoard(board: BoardData): Promise<void> {
  const res = await fetch("/api/board", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(board),
    credentials: "include",
  });
  checkStatus(res);
}
