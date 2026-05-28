"use client";

import { useEffect, useState } from "react";
import { LogOut, User } from "lucide-react";

import { Button } from "@/components/ui/button";
import { getSession, logout } from "@/lib/api";
import type { AuthSession } from "@/types/api";

export function AuthStatus() {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadSession() {
      try {
        const current = await getSession();
        if (active) {
          setSession(current);
        }
      } catch {
        if (active) {
          setSession(null);
        }
      }
    }

    void loadSession();
    return () => {
      active = false;
    };
  }, []);

  async function handleLogout() {
    setBusy(true);
    try {
      await logout();
    } finally {
      window.location.assign("/login");
    }
  }

  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-white/10 bg-white/5 p-3">
      <div className="flex items-center gap-2">
        <User className="size-4 text-white/60" />
        <div className="grid gap-0.5">
          <span className="text-[0.65rem] font-bold uppercase tracking-wider text-white/50">
            当前会话
          </span>
          <span className="text-sm font-semibold text-white">
            {session?.user.username || "admin"}
          </span>
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        className="text-white/70 hover:bg-white/10 hover:text-white"
        disabled={busy}
        onClick={() => void handleLogout()}
      >
        <LogOut className="size-3.5" />
        {busy ? "退出中" : "退出"}
      </Button>
    </div>
  );
}
