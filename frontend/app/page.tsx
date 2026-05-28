import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { WorkbenchHero } from "@/components/workbench-layout";
import { getCapabilitiesServer } from "@/lib/server-api";
import { requireAuthenticatedPage } from "@/lib/server-auth";
import {
  HotSectors,
  LatestNews,
} from "@/components/dashboard-widgets";

const LIVE_ENTRIES = [
  { href: "/screener", title: "选股研究", copy: "多维度筛选候选标的" },
  { href: "/diagnosis", title: "诊股报告", copy: "AI 驱动的技术面诊断" },
  { href: "/factors", title: "因子研究", copy: "因子快照与 IC 排名" },
  { href: "/portfolio", title: "组合研究", copy: "权重优化与风险统计" },
];

export default async function HomePage() {
  await requireAuthenticatedPage("/");
  const capabilities = await getCapabilitiesServer();
  const ready = capabilities.filter((item) => item.status === "ready");

  return (
    <div className="grid gap-6">
      <WorkbenchHero
        eyebrow="研究总览"
        title="A 股研究工作台"
        description="一站式 A 股研究终端。"
        metrics={[
          {
            label: "可用能力",
            value: ready.length,
          },
          {
            label: "受限能力",
            value: capabilities.length - ready.length,
          },
        ]}
        meta={["AI 驱动", "实时数据"]}
      />

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              热门板块
            </span>
            <CardTitle className="font-display">概念板块</CardTitle>
          </CardHeader>
          <CardContent>
            <HotSectors />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              最新资讯
            </span>
            <CardTitle className="font-display">市场快讯</CardTitle>
          </CardHeader>
          <CardContent>
            <LatestNews />
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">研究入口</span>
            <CardTitle className="font-display">可执行研究闭环</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {LIVE_ENTRIES.map((item) => (
                <Link
                  className="flex items-center justify-between rounded-lg border border-border p-3 transition-colors hover:bg-muted/50"
                  href={item.href}
                  key={item.href}
                >
                  <div>
                    <strong className="text-sm">{item.title}</strong>
                    <p className="text-xs text-muted-foreground">{item.copy}</p>
                  </div>
                  <ArrowRight className="size-4 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">已启用能力</span>
            <CardTitle className="font-display">可用模块</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {ready.map((capability) => (
                <div className="rounded-lg border border-border p-3" key={capability.name}>
                  <strong className="text-sm">{capability.label}</strong>
                  <p className="mt-1 text-xs text-muted-foreground">{capability.summary}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
