"use client";

import { useEffect, useState } from "react";
import { isLoggedIn } from "@/lib/auth";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginPage } from "@/components/LoginPage";

export const AuthWrapper = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setIsAuthenticated(isLoggedIn());
    setMounted(true);
  }, []);

  if (!mounted) return null;
  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }
  return <KanbanBoard onLogout={() => setIsAuthenticated(false)} />;
};
