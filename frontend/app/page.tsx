import Link from "next/link";

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
    <>
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

      <section className="dashboard-grid">
        <aside className="panel">
          <div className="eyebrow">研究入口</div>
          <h2 className="panel-title">可执行研究闭环</h2>
          <div className="action-grid">
            {LIVE_ENTRIES.map((item) => (
              <Link className="action-card" href={item.href} key={item.href}>
                <strong>{item.title}</strong>
                <p>{item.copy}</p>
              </Link>
            ))}
          </div>
        </aside>

        <article className="panel">
          <div className="eyebrow">能力地图</div>
          <h2 className="panel-title">真实接口清单</h2>
          <div className="status-list">
            {capabilities.map((capability) => (
              <div className="status-item" data-status={capability.status} key={capability.name}>
                <div className="status-head">
                  <strong>{capability.label}</strong>
                  <span className="status-pill">{displayCapabilityStatus(capability.status)}</span>
                </div>
                <p>{capability.summary}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">接口契约</div>
          <h2 className="panel-title">接口事实源</h2>
          <div className="status-list">
            <div className="fact-item">运行时接口文档：/api/v1/openapi.json</div>
            <div className="fact-item">静态契约文件：openapi.json</div>
            <div className="fact-item">
              除健康检查和登录外，业务接口均通过受保护访问链路调用。
            </div>
          </div>
        </article>
      </section>
    </>
  );
}
