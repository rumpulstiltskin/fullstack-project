"use client";

import { useEffect, useState } from "react";
import { getToken } from "@/lib/auth";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginPage } from "@/components/LoginPage";

export const AuthWrapper = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    setIsAuthenticated(!!getToken());
    setIsChecking(false);
  }, []);

  if (isChecking) return null;
  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }
  return <KanbanBoard onLogout={() => setIsAuthenticated(false)} />;
};
