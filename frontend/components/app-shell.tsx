"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AuthStatus } from "@/components/auth-status";

const NAV_ITEMS = [
  {
    href: "/",
    label: "Overview",
    badge: "Cockpit",
    summary: "查看真实完成度、当前入口和双运行时边界。",
  },
  {
    href: "/backtests",
    label: "Backtests",
    badge: "Live",
    summary: "当前最完整的工作台链路，已接通 Flask 回测 API。",
  },
  {
    href: "/market",
    label: "Market",
    badge: "Live Data",
    summary: "真实消费 AkShare/Jin10 后端接口，展示行情、板块与 intelligence。",
  },
  {
    href: "/screener",
    label: "Screener",
    badge: "Skeleton",
    summary: "保留新架构入口，但东方财富选股链路尚未迁入。",
  },
  {
    href: "/diagnosis",
    label: "Diagnosis",
    badge: "Skeleton",
    summary: "AI 诊股仍处于后端边界预留阶段。",
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  if (pathname === "/login") {
    return (
      <div className="app-shell">
        <div className="shell-auth-frame">{children}</div>
      </div>
    );
  }

  const currentItem = NAV_ITEMS.find((item) => item.href === pathname) || NAV_ITEMS[0];

  return (
    <div className="app-shell">
      <div className="shell-frame">
        <header className="shell-topbar">
          <div className="shell-brand-block">
            <div className="shell-brand">
              <div className="shell-mark">Sensitive Stock</div>
              <div className="shell-tag">Research Desk / Dual Runtime</div>
            </div>
            <div className="shell-brand-note">
              用更诚实的状态表达，把已迁移能力做成真正可操作的研究工作台。
            </div>
          </div>

          <div className="shell-toolbar">
            <AuthStatus />
            <nav className="shell-nav" aria-label="Primary">
              {NAV_ITEMS.map((item) => (
                <Link
                  className="nav-link"
                  data-active={pathname === item.href}
                  href={item.href}
                  key={item.href}
                >
                  <span>{item.label}</span>
                  <small>{item.badge}</small>
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <div className="shell-subbar">
          <div className="shell-context">
            <span className="shell-context-title">{currentItem.label}</span>
            <span className="shell-context-copy">{currentItem.summary}</span>
          </div>
          <div className="shell-status-strip">
            <span className="shell-status-chip" data-tone="positive">
              Backtests live
            </span>
            <span className="shell-status-chip" data-tone="neutral">
              Market connected
            </span>
            <span className="shell-status-chip" data-tone="warning">
              Screener / Diagnosis skeleton
            </span>
          </div>
        </div>

        <main className="shell-body">{children}</main>
      </div>
    </div>
  );
}
