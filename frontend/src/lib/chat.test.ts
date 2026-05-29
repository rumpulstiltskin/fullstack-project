import { sendMessage } from "@/lib/chat";

describe("sendMessage", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it("posts to /api/chat with correct shape and credentials", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: "Hello!", board_update: null }),
    } as Response);

    const result = await sendMessage("Current");

    expect(fetch).toHaveBeenCalledWith("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_message: "Current" }),
      credentials: "include",
    });
    expect(result).toEqual({ message: "Hello!", board_update: null });
  });

  it("throws on non-2xx response", async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: false, status: 502 } as Response);
    await expect(sendMessage("Hello")).rejects.toThrow("502");
  });
});
