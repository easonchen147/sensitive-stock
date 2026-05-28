import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { WorkbenchHero } from "@/components/workbench-layout";
import { displayCapabilityStatus } from "@/lib/display";
import { getCapabilitiesServer } from "@/lib/server-api";
import { requireAuthenticatedPage } from "@/lib/server-auth";

const LIVE_ENTRIES = [
  { href: "/screener", title: "选股研究", copy: "运行结构化筛选，并把候选结果交接到回测验证。" },
  { href: "/diagnosis", title: "诊股报告", copy: "生成带行情上下文的结构化诊断报告。" },
  { href: "/factors", title: "因子研究", copy: "分析因子快照和 IC 排名变化。" },
  { href: "/portfolio", title: "组合研究", copy: "为选定标的篮子生成目标权重与风险统计。" },
];

export default async function HomePage() {
  await requireAuthenticatedPage("/");
  const capabilities = await getCapabilitiesServer();
  const ready = capabilities.filter((item) => item.status === "ready");
  const limited = capabilities.filter((item) => item.status === "limited");

  return (
    <div className="grid gap-6">
      <WorkbenchHero
        eyebrow="研究总览"
        title="A 股研究工作台"
        description="把行情情报、预测复盘、回测验证、选股、诊股、因子和组合优化放在同一套研究终端里，首页只展示真实可调用的功能入口。"
        metrics={[
          {
            label: "可用能力",
            value: ready.length,
            note: "已具备真实接口和页面入口。",
          },
          {
            label: "受限能力",
            value: limited.length,
            note: "当前没有受限模块时保持为 0。",
          },
        ]}
        meta={["中文投研终端", "接口契约", "受保护访问"]}
      />

      <section className="grid gap-6 lg:grid-cols-3">
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
            <span className="text-xs font-bold uppercase tracking-wider text-primary">能力地图</span>
            <CardTitle className="font-display">真实接口清单</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {capabilities.map((capability) => (
                <div className="rounded-lg border border-border p-3" key={capability.name}>
                  <div className="flex items-center justify-between">
                    <strong className="text-sm">{capability.label}</strong>
                    <Badge variant={capability.status === "ready" ? "default" : "secondary"}>
                      {displayCapabilityStatus(capability.status)}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{capability.summary}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">接口契约</span>
            <CardTitle className="font-display">接口事实源</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              <div className="rounded-lg border border-border p-3 text-sm">运行时接口文档：/api/v1/openapi.json</div>
              <div className="rounded-lg border border-border p-3 text-sm">静态契约文件：openapi.json</div>
              <div className="rounded-lg border border-border p-3 text-sm">
                除健康检查和登录外，业务接口均通过受保护访问链路调用。
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
