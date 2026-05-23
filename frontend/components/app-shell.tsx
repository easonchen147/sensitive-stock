"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AuthStatus } from "@/components/auth-status";

const NAV_ITEMS = [
  {
    href: "/",
    label: "研究总览",
    badge: "中枢",
    summary: "接口清单、研究入口、风险提示和预测复盘入口。",
  },
  {
    href: "/backtests",
    label: "回测验证",
    badge: "验证",
    summary: "策略执行、交易假设、成本风控和结构化报告。",
  },
  {
    href: "/market",
    label: "行情预测",
    badge: "情报",
    summary: "行情、快讯、模型预测、历史详情和评估闭环。",
  },
  {
    href: "/screener",
    label: "选股研究",
    badge: "筛选",
    summary: "结构化条件、自然语言解释、导出字段和回测交接。",
  },
  {
    href: "/diagnosis",
    label: "诊股报告",
    badge: "诊断",
    summary: "行情上下文、指标摘要、诊断段落和风险提示。",
  },
  {
    href: "/factors",
    label: "因子研究",
    badge: "因子",
    summary: "最新因子、相关性排名、窗口信息和摘要统计。",
  },
  {
    href: "/portfolio",
    label: "组合研究",
    badge: "配置",
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
              统一入口服务 A 股研究、预测、验证与组合配置，所有可见模块均有接口支撑。
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
              数据通路
            </span>
            <span className="shell-status-chip" data-tone="neutral">
              模型预测
            </span>
            <span className="shell-status-chip" data-tone="positive">
              回测验证
            </span>
          </div>
        </div>

        <main className="shell-body">{children}</main>
      </div>
    </div>
  );
}
