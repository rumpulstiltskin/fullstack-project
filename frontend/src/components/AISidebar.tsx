"use client";

import { useEffect, useRef, useState } from "react";
import { sendMessage, type AIResponse, type ChatMessage } from "@/lib/chat";
import type { BoardData } from "@/lib/kanban";

type AISidebarProps = {
  isOpen: boolean;
  onBoardUpdate: (board: BoardData) => void;
};

export const AISidebar = ({ isOpen, onBoardUpdate }: AISidebarProps) => {
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [history, isThinking]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const message = input.trim();
    if (!message || isThinking) return;

    const userMsg: ChatMessage = { role: "user", content: message };
    const nextHistory = [...history, userMsg];
    setHistory(nextHistory);
    setInput("");
    setIsThinking(true);

    try {
      const response: AIResponse = await sendMessage(history, message);
      setHistory([...nextHistory, { role: "assistant", content: response.message }]);
      if (response.board_update) {
        onBoardUpdate(response.board_update);
      }
    } catch {
      setHistory([
        ...nextHistory,
        { role: "assistant", content: "Something went wrong. Please try again." },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <aside
      aria-label="AI assistant"
      className={`fixed right-0 top-0 z-50 flex h-screen w-[360px] flex-col border-l border-[var(--stroke)] bg-white shadow-2xl transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex items-center border-b border-[var(--stroke)] px-5 py-4">
        <p className="text-sm font-semibold uppercase tracking-widest text-[var(--navy-dark)]">
          AI Assistant
        </p>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {history.length === 0 && !isThinking && (
          <p className="mt-8 text-center text-xs text-[var(--gray-text)]">
            Ask me to add, move, or rename cards on your board.
          </p>
        )}
        {history.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-[var(--primary-blue)] text-white"
                  : "bg-[var(--surface)] text-[var(--navy-dark)]"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {isThinking && (
          <div className="flex justify-start">
            <div
              data-testid="thinking-indicator"
              className="flex items-center gap-1 rounded-2xl bg-[var(--surface)] px-4 py-3"
            >
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--gray-text)] [animation-delay:0ms]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--gray-text)] [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--gray-text)] [animation-delay:300ms]" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-[var(--stroke)] px-4 py-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI..."
            disabled={isThinking}
            className="flex-1 rounded-full border border-[var(--stroke)] bg-[var(--surface)] px-4 py-2 text-sm text-[var(--navy-dark)] placeholder:text-[var(--gray-text)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)] disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isThinking}
            className="rounded-full bg-[var(--primary-blue)] px-4 py-2 text-xs font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>
    </aside>
  );
};
