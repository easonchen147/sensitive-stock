import { MarketWorkbench } from "@/components/market-workbench";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function MarketPage() {
  await requireAuthenticatedPage("/market");

  return (
    <>
      <section className="hero">
        <article className="hero-card">
          <div className="eyebrow">Market Intelligence</div>
          <h1 className="hero-title">把已经迁好的行情与快讯 API，真正变成前端工作台。</h1>
          <p className="hero-copy">
            这一页现在会直接消费 backend market/news 接口，而不是继续停留在 placeholder。你能在这里看到
            AkShare 报价、热门板块、Jin10 快讯和当前规则式 intelligence 的真实返回结果。
          </p>
        </article>

        <aside className="hero-card status-rail">
          <div className="eyebrow">State Boundary</div>
          <h2 className="panel-title">What this page is, and is not</h2>
          <div className="status-list">
            <div className="status-item" data-status="migrated">
              <div className="status-head">
                <strong>已完成</strong>
                <span className="status-pill">api connected</span>
              </div>
              <p>市场页已经真实接入 backend 行情、板块、快讯与 intelligence API。</p>
            </div>
            <div className="status-item" data-status="skeleton">
              <div className="status-head">
                <strong>未完成</strong>
                <span className="status-pill">not AI yet</span>
              </div>
              <p>当前 intelligence 仍是规则式关键词与板块提示，不会被描述成完整 AI 市场研判。</p>
            </div>
          </div>
        </aside>
      </section>

      <MarketWorkbench />
    </>
  );
}
