type CapabilityStatusPanelProps = {
  eyebrow: string;
  title: string;
  summary: string;
  status: "ready" | "limited" | "disabled";
  route: string;
  availableNow: string[];
  blockedBy: string[];
  nextStep: string;
};

const STATUS_LABELS = {
  ready: "可用",
  limited: "受限",
  disabled: "停用",
};

export function CapabilityStatusPanel({
  eyebrow,
  title,
  summary,
  status,
  route,
  availableNow,
  blockedBy,
  nextStep,
}: CapabilityStatusPanelProps) {
  return (
    <>
      <section className="hero">
        <article className="hero-card">
          <div className="eyebrow">{eyebrow}</div>
          <h1 className="hero-title">{title}</h1>
          <p className="hero-copy">{summary}</p>

          <div className="hero-stat-strip">
            <div className="metric-card">
              <span className="metric-label">能力入口</span>
              <div className="metric-value">{route}</div>
              <div className="metric-note">当前入口必须由真实接口支撑</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">状态</span>
              <div className="metric-value">{STATUS_LABELS[status]}</div>
              <div className="metric-note">只展示运行态，不展示交付过程标签</div>
            </div>
          </div>
        </article>

        <aside className="hero-card status-rail">
          <div className="eyebrow">交付状态</div>
          <h2 className="panel-title">运行状态</h2>
          <div className="status-list">
            <div className="status-item" data-status={status}>
              <div className="status-head">
                <strong>当前阶段</strong>
                <span className="status-pill">{STATUS_LABELS[status]}</span>
              </div>
              <p>{summary}</p>
            </div>
            <div className="status-item" data-status="limited">
              <div className="status-head">
                <strong>下一步</strong>
                <span className="status-pill">受限项</span>
              </div>
              <p>{nextStep}</p>
            </div>
          </div>
        </aside>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">当前可用</div>
          <h2 className="panel-title">已具备的边界</h2>
          <div className="status-list">
            {availableNow.map((item) => (
              <div className="fact-item" key={item}>
                {item}
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">受限说明</div>
          <h2 className="panel-title">当前受限项</h2>
          <div className="status-list">
            {blockedBy.map((item) => (
              <div className="fact-item" key={item}>
                {item}
              </div>
            ))}
          </div>
        </article>
      </section>
    </>
  );
}
