type CapabilityPlaceholderProps = {
  eyebrow: string;
  title: string;
  summary: string;
  status: "skeleton" | "planned" | "migrated";
  route: string;
  availableNow: string[];
  blockedBy: string[];
  nextStep: string;
};

export function CapabilityPlaceholder({
  eyebrow,
  title,
  summary,
  status,
  route,
  availableNow,
  blockedBy,
  nextStep,
}: CapabilityPlaceholderProps) {
  return (
    <>
      <section className="hero">
        <article className="hero-card">
          <div className="eyebrow">{eyebrow}</div>
          <h1 className="hero-title">{title}</h1>
          <p className="hero-copy">{summary}</p>

          <div className="hero-stat-strip">
            <div className="metric-card">
              <span className="metric-label">Capability</span>
              <div className="metric-value">{route}</div>
              <div className="metric-note">当前入口已预留在新前端中</div>
            </div>
            <div className="metric-card">
              <span className="metric-label">Status</span>
              <div className="metric-value">{status}</div>
              <div className="metric-note">不会把未迁链路伪装成已完成</div>
            </div>
          </div>
        </article>

        <aside className="hero-card status-rail">
          <div className="eyebrow">Delivery Truth</div>
          <h2 className="panel-title">What is real right now</h2>
          <div className="status-list">
            <div className="status-item" data-status={status}>
              <div className="status-head">
                <strong>当前阶段</strong>
                <span className="status-pill">{status}</span>
              </div>
              <p>{summary}</p>
            </div>
            <div className="status-item" data-status="planned">
              <div className="status-head">
                <strong>下一步</strong>
                <span className="status-pill">next</span>
              </div>
              <p>{nextStep}</p>
            </div>
          </div>
        </aside>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">Available Now</div>
          <h2 className="panel-title">已具备的边界</h2>
          <div className="status-list">
            {availableNow.map((item) => (
              <div className="placeholder-item" key={item}>
                {item}
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">Still Missing</div>
          <h2 className="panel-title">尚未迁入的真实依赖</h2>
          <div className="status-list">
            {blockedBy.map((item) => (
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
