import { sendMessage } from "@/lib/chat";

vi.mock("@/lib/auth", () => ({
  getToken: vi.fn().mockReturnValue("test-token"),
}));

describe("sendMessage", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it("posts to /api/chat with correct shape and auth header", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: "Hello!", board_update: null }),
    } as Response);

    const history = [{ role: "user" as const, content: "Previous" }];
    const result = await sendMessage(history, "Current");

    expect(fetch).toHaveBeenCalledWith("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer test-token",
      },
      body: JSON.stringify({ history, user_message: "Current" }),
    });
    expect(result).toEqual({ message: "Hello!", board_update: null });
  });

  it("throws on non-2xx response", async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: false, status: 502 } as Response);
    await expect(sendMessage([], "Hello")).rejects.toThrow("502");
  });
});
