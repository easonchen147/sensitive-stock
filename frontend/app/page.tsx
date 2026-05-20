import Link from "next/link";

import { getCapabilitiesServer } from "@/lib/server-api";
import { requireAuthenticatedPage } from "@/lib/server-auth";

const LIVE_ENTRIES = [
  {
    href: "/backtests",
    eyebrow: "Primary Flow",
    title: "回测工作台",
    copy: "已接通策略预设、执行假设、交易成本、风险控制与结构化回测结果。",
  },
  {
    href: "/market",
    eyebrow: "Market Intelligence",
    title: "行情工作台",
    copy: "直接消费 AkShare/Jin10 后端接口，查看报价、板块、快讯与关键词提示。",
  },
];

export default async function HomePage() {
  await requireAuthenticatedPage("/");
  const capabilities = await getCapabilitiesServer();
  const migrated = capabilities.filter((item) => item.status === "migrated");
  const skeletons = capabilities.filter((item) => item.status !== "migrated");

  return (
    <>
      <section className="hero">
        <article className="hero-card">
          <div className="eyebrow">Operational Cockpit</div>
          <h1 className="hero-title">把“已经做出来的能力”做成真正能用的研究工作台。</h1>
          <p className="hero-copy">
            当前默认入口已经切换到 Next.js + Flask。这个 cockpit 不再只讲迁移故事，而是明确告诉你：
            哪些链路已经真实可用、哪些只是边界已立、以及现在最值得直接进入的两个工作区。
          </p>

          <div className="hero-stats">
            <div className="metric-card">
              <span className="metric-label">Migrated</span>
              <div className="metric-value">{migrated.length}</div>
              <div className="metric-note">真正接上新架构并可验证的能力</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Skeleton</span>
              <div className="metric-value">{skeletons.length}</div>
              <div className="metric-note">已建入口和边界，但未迁业务执行链</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Frontend</span>
              <div className="metric-value">Next.js</div>
              <div className="metric-note">App Router / React 19.2.4</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Backend</span>
              <div className="metric-value">Flask</div>
              <div className="metric-note">Versioned API + legacy adapters</div>
            </div>
          </div>
        </article>

        <aside className="hero-card status-rail">
          <div className="eyebrow">Use Right Now</div>
          <h2 className="panel-title">Recommended entry points</h2>
          <div className="action-grid">
            {LIVE_ENTRIES.map((item) => (
              <Link className="action-card" href={item.href} key={item.href}>
                <span className="metric-label">{item.eyebrow}</span>
                <strong>{item.title}</strong>
                <p>{item.copy}</p>
              </Link>
            ))}
          </div>
        </aside>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">Capability Truth Map</div>
          <h2 className="panel-title">Backend capability inventory, rendered honestly</h2>
          <p className="panel-subtitle">
            首页直接读取 `/api/v1/capabilities`。页面状态表达必须和真实完成度一致，所以 migrated
            与 skeleton 会明确区分，不再用模糊文案混过去。
          </p>
          <div className="status-list">
            {capabilities.map((capability) => (
              <div className="status-item" data-status={capability.status} key={capability.name}>
                <div className="status-head">
                  <strong>{capability.label}</strong>
                  <span className="status-pill">{capability.status}</span>
                </div>
                <p>{capability.summary}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">Phase-One Boundaries</div>
          <h2 className="panel-title">What changed after the split runtime</h2>
          <div className="timeline">
            {[
              "默认用户入口已不再依赖旧 Streamlit 页面，而由 Next.js 接管。",
              "回测主链路已经迁通并持续增强，是当前最完整的工作台。",
              "市场 backend 服务已迁移完成，这一轮前端会正式消费它们。",
              "条件选股和 AI 诊股依旧保留 skeleton 状态，不会伪装成已完成。",
            ].map((item, index) => (
              <div className="timeline-step" key={item}>
                <div className="timeline-index">0{index + 1}</div>
                <div className="supporting-copy">{item}</div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">Workbench Surface</div>
          <h2 className="panel-title">这轮真正完成了什么</h2>
          <div className="placeholder-grid">
            <div className="placeholder-card">
              <h3>Backtests</h3>
              <p>用更强的表单引导、假设摘要和结果解释，把主链路做成专业工作台。</p>
            </div>
            <div className="placeholder-card">
              <h3>Market</h3>
              <p>不再停留在 placeholder，而是直接读取后端行情、板块、快讯和 intelligence。</p>
            </div>
            <div className="placeholder-card">
              <h3>Capability Briefs</h3>
              <p>screener / diagnosis 继续保留 skeleton，但状态表达会更清晰、更一致。</p>
            </div>
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">What Stays Out</div>
          <h2 className="panel-title">本轮刻意不做的事</h2>
          <div className="status-list">
            {[
              "不引入无关大重构，也不在这轮迁移真实的东方财富选股执行链路。",
              "不把 AI 诊股页面伪装成已可运行功能，仍明确标注为 skeleton。",
              "不把回测扩大成异步任务队列、组合撮合引擎或完整策略 IDE。",
            ].map((item) => (
              <div className="placeholder-item" key={item}>
                {item}
              </div>
            ))}
          </div>
        </article>
      </section>
    </>
  );
}
