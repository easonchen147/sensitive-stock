"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Briefcase,
  FlaskConical,
  LayoutDashboard,
  LineChart,
  Search,
  Stethoscope,
} from "lucide-react";

import { AuthStatus } from "@/components/auth-status";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

const NAV_ITEMS = [
  {
    href: "/",
    label: "研究总览",
    badge: "中枢",
    icon: LayoutDashboard,
    summary: "接口清单、研究入口、风险提示和预测复盘入口。",
  },
  {
    href: "/backtests",
    label: "回测验证",
    badge: "验证",
    icon: FlaskConical,
    summary: "策略执行、交易假设、成本风控和结构化报告。",
  },
  {
    href: "/market",
    label: "行情预测",
    badge: "情报",
    icon: LineChart,
    summary: "行情、快讯、模型预测、历史详情和评估闭环。",
  },
  {
    href: "/screener",
    label: "选股研究",
    badge: "筛选",
    icon: Search,
    summary: "结构化条件、自然语言解释、导出字段和回测交接。",
  },
  {
    href: "/diagnosis",
    label: "诊股报告",
    badge: "诊断",
    icon: Stethoscope,
    summary: "行情上下文、指标摘要、诊断段落和风险提示。",
  },
  {
    href: "/factors",
    label: "因子研究",
    badge: "因子",
    icon: BarChart3,
    summary: "最新因子、相关性排名、窗口信息和摘要统计。",
  },
  {
    href: "/portfolio",
    label: "组合研究",
    badge: "配置",
    icon: Briefcase,
    summary: "组合优化目标、权重分配、统计指标和风险提示。",
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/login") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas p-4">
        <div className="w-full max-w-5xl">{children}</div>
      </div>
    );
  }

  const currentItem = NAV_ITEMS.find((item) => item.href === pathname) || NAV_ITEMS[0];

  return (
    <SidebarProvider>
      <Sidebar className="border-r border-sidebar-border bg-rail text-white">
        <SidebarHeader className="p-4">
          <div className="grid gap-2">
            <h1 className="font-display text-lg font-bold tracking-tight">
              敏感股票研究台
            </h1>
            <p className="text-xs text-white/60">
              预测 · 回测 · 因子 · 组合
            </p>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-white/50">
            统一入口服务 A 股研究、预测、验证与组合配置，所有可见模块均有接口支撑。
          </p>
        </SidebarHeader>

        <Separator className="bg-white/10" />

        <SidebarContent className="px-2 py-4">
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                {NAV_ITEMS.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href;
                  return (
                    <SidebarMenuItem key={item.href}>
                      <SidebarMenuButton
                        asChild
                        isActive={isActive}
                        className="h-11 text-white/80 hover:bg-white/10 hover:text-white data-[active=true]:bg-white/15 data-[active=true]:text-white"
                      >
                        <Link href={item.href}>
                          <Icon className="size-4 shrink-0" />
                          <span className="font-semibold">{item.label}</span>
                          <Badge
                            variant="secondary"
                            className="ml-auto bg-white/10 text-[0.65rem] text-white/60"
                          >
                            {item.badge}
                          </Badge>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <Separator className="bg-white/10" />

        <SidebarFooter className="p-4">
          <AuthStatus />
        </SidebarFooter>
      </Sidebar>

      <SidebarInset>
        <header className="flex h-14 items-center gap-4 border-b border-line bg-surface px-6">
          <SidebarTrigger className="size-8" />
          <Separator orientation="vertical" className="h-6" />
          <div className="flex flex-1 items-center justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm font-bold text-ink">{currentItem.label}</p>
              <p className="truncate text-xs text-muted">{currentItem.summary}</p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Badge variant="outline" className="border-positive/25 bg-positive-soft text-positive">
                数据通路
              </Badge>
              <Badge variant="outline" className="bg-neutral-soft text-muted">
                模型预测
              </Badge>
              <Badge variant="outline" className="border-positive/25 bg-positive-soft text-positive">
                回测验证
              </Badge>
            </div>
          </div>
        </header>

        <main className="flex-1 bg-surface-muted p-6">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
