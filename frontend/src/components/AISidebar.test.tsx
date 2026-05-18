import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AISidebar } from "@/components/AISidebar";
import { sendMessage } from "@/lib/chat";
import type { AIResponse } from "@/lib/chat";

vi.mock("@/lib/chat");

describe("AISidebar", () => {
  it("renders empty state prompt when open", () => {
    render(<AISidebar isOpen={true} onBoardUpdate={vi.fn()} />);
    expect(screen.getByText(/ask me to add/i)).toBeInTheDocument();
  });

  it("sends a message and displays the AI reply", async () => {
    vi.mocked(sendMessage).mockResolvedValue({
      message: "Done!",
      board_update: null,
    });

    render(<AISidebar isOpen={true} onBoardUpdate={vi.fn()} />);
    await userEvent.type(screen.getByPlaceholderText(/ask the ai/i), "Hello");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("Hello")).toBeInTheDocument();
    expect(await screen.findByText("Done!")).toBeInTheDocument();
  });

  it("shows thinking indicator while request is in flight then hides it", async () => {
    let resolve!: (v: AIResponse) => void;
    vi.mocked(sendMessage).mockImplementation(
      () => new Promise((r) => (resolve = r))
    );

    render(<AISidebar isOpen={true} onBoardUpdate={vi.fn()} />);
    await userEvent.type(screen.getByPlaceholderText(/ask the ai/i), "Hello");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(screen.getByTestId("thinking-indicator")).toBeInTheDocument();

    resolve({ message: "Hi!", board_update: null });
    await screen.findByText("Hi!");
    expect(screen.queryByTestId("thinking-indicator")).not.toBeInTheDocument();
  });

  it("calls onBoardUpdate when AI returns a board_update", async () => {
    const mockBoard = { columns: [], cards: {} };
    const onBoardUpdate = vi.fn();
    vi.mocked(sendMessage).mockResolvedValue({
      message: "Updated!",
      board_update: mockBoard,
    });

    render(<AISidebar isOpen={true} onBoardUpdate={onBoardUpdate} />);
    await userEvent.type(screen.getByPlaceholderText(/ask the ai/i), "Add a card");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await screen.findByText("Updated!");
    expect(onBoardUpdate).toHaveBeenCalledWith(mockBoard);
  });
});
