"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AuthStatus } from "@/components/auth-status";

const NAV_ITEMS = [
  {
    href: "/",
    label: "Overview",
    badge: "Cockpit",
    summary: "Capability inventory, API status, and research workflow entry points.",
  },
  {
    href: "/backtests",
    label: "Backtests",
    badge: "Live",
    summary: "AKQuant-backed strategy execution and structured reports.",
  },
  {
    href: "/market",
    label: "Market",
    badge: "Live Data",
    summary: "AkShare and Jin10 market intelligence from the Flask backend.",
  },
  {
    href: "/screener",
    label: "Screener",
    badge: "Migrated",
    summary: "Structured filters, natural-language interpretation, export rows, and backtest handoff.",
  },
  {
    href: "/diagnosis",
    label: "Diagnosis",
    badge: "Migrated",
    summary: "Market context, indicator summaries, diagnosis sections, and degraded metadata.",
  },
  {
    href: "/factors",
    label: "Factors",
    badge: "Migrated",
    summary: "Factor analysis API with latest factors, IC ranking, and window metadata.",
  },
  {
    href: "/portfolio",
    label: "Portfolio",
    badge: "Migrated",
    summary: "Portfolio optimizer API with objectives, allocations, and statistics.",
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
              <div className="shell-tag">Research Desk / OpenAPI Platform</div>
            </div>
            <div className="shell-brand-note">
              All primary research workbenches are now backed by Flask APIs and the shared
              OpenAPI contract.
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
            <span className="shell-status-chip" data-tone="positive">
              Research APIs migrated
            </span>
          </div>
        </div>

        <main className="shell-body">{children}</main>
      </div>
    </div>
  );
}
