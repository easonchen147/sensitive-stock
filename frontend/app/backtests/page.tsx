import { BacktestConsole } from "@/components/backtest-console";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function BacktestsPage() {
  await requireAuthenticatedPage("/backtests");

  return (
    <>
      <section className="hero">
        <article className="hero-card">
          <div className="eyebrow">Backtest Workbench</div>
          <h1 className="hero-title">更容易配置，也更容易解释结果的 AKQuant-inspired 回测台。</h1>
          <p className="hero-copy">
            这里继续复用现有 Flask + legacy 引擎链路，但把交互升级成更专业的研究工作台：策略预设、
            参数说明、执行/成本/风控假设、结果 insight 和交易解释都在同一个页面里闭环。
          </p>
        </article>

        <aside className="hero-card status-rail">
          <div className="eyebrow">What This Optimizes</div>
          <h2 className="panel-title">Focus areas in this wave</h2>
          <div className="status-list">
            <div className="status-item" data-status="migrated">
              <div className="status-head">
                <strong>Input Guidance</strong>
                <span className="status-pill">grouped</span>
              </div>
              <p>把市场、策略、执行、成本和风控分组，减少长表单心智负担。</p>
            </div>
            <div className="status-item" data-status="migrated">
              <div className="status-head">
                <strong>Assumptions</strong>
                <span className="status-pill">clearer</span>
              </div>
              <p>执行模式、手数、税费与止损止盈不再隐藏在输入项背后，而会在结果里重复回显。</p>
            </div>
            <div className="status-item" data-status="migrated">
              <div className="status-head">
                <strong>Interpretability</strong>
                <span className="status-pill">richer</span>
              </div>
              <p>除了收益指标，还会提供风险画像、相对基准 insight 和交易执行摘要。</p>
            </div>
          </div>
        </aside>
      </section>

      <BacktestConsole />
    </>
  );
}
