"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AuthStatus } from "@/components/auth-status";

const NAV_ITEMS = [
  {
    href: "/",
    label: "研究总览",
    badge: "总览",
    summary: "能力地图、接口状态、预测复盘和研究工作流入口。",
  },
  {
    href: "/backtests",
    label: "回测验证",
    badge: "已接入",
    summary: "基于 AKQuant 的策略执行、交易假设和结构化报告。",
  },
  {
    href: "/market",
    label: "行情预测",
    badge: "多源资讯",
    summary: "AkShare 行情、多源快讯、DeepSeek 预测和评估闭环。",
  },
  {
    href: "/screener",
    label: "选股研究",
    badge: "已迁移",
    summary: "结构化条件、自然语言解释、导出字段和回测回灌。",
  },
  {
    href: "/diagnosis",
    label: "诊股报告",
    badge: "已迁移",
    summary: "行情上下文、指标摘要、诊断段落和降级元数据。",
  },
  {
    href: "/factors",
    label: "因子研究",
    badge: "已迁移",
    summary: "最新因子、IC 排名、窗口元数据和摘要统计。",
  },
  {
    href: "/portfolio",
    label: "组合研究",
    badge: "已迁移",
    summary: "组合优化目标、权重分配、统计指标和风险提示。",
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
              <div className="shell-mark">敏感股票研究台</div>
              <div className="shell-tag">预测 · 回测 · 因子 · 组合</div>
            </div>
            <div className="shell-brand-note">
              统一使用 Flask 后端、受保护接口和全局 OpenAPI 契约，服务 A 股研究、预测与验证闭环。
            </div>
          </div>

          <div className="shell-toolbar">
            <AuthStatus />
            <nav className="shell-nav" aria-label="主导航">
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
              回测已接入
            </span>
            <span className="shell-status-chip" data-tone="neutral">
              行情已连接
            </span>
            <span className="shell-status-chip" data-tone="positive">
              研究接口已迁移
            </span>
          </div>
        </div>

        <main className="shell-body">{children}</main>
      </div>
    </div>
  );
}
