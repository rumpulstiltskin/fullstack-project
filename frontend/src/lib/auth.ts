const LOGGED_IN_KEY = "logged_in";

export async function login(username: string, password: string): Promise<void> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Invalid credentials");
  }
  const data = await res.json();
  if (!data.ok) {
    throw new Error("Invalid credentials");
  }
  localStorage.setItem(LOGGED_IN_KEY, "1");
}

export async function logout(): Promise<void> {
  localStorage.removeItem(LOGGED_IN_KEY);
  await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "include",
  }).catch(() => {});
}

export function isLoggedIn(): boolean {
  return localStorage.getItem(LOGGED_IN_KEY) === "1";
}

export function clearLoggedIn(): void {
  localStorage.removeItem(LOGGED_IN_KEY);
}
