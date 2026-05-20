"use client";

import { useEffect, useState } from "react";

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
    <div className="auth-toolbar">
      <div className="auth-toolbar-copy">
        <span className="auth-toolbar-label">Session</span>
        <strong>{session?.user.username || "admin"}</strong>
      </div>
      <button className="ghost-button" disabled={busy} type="button" onClick={() => void handleLogout()}>
        {busy ? "退出中" : "退出登录"}
      </button>
    </div>
  );
}
