import type { CapabilityMetadata } from "@/types/api";
import { displayText } from "@/lib/display";

export type WorkflowState = "loading" | "empty" | "degraded" | "error" | "ready";

const STATE_LABELS: Record<WorkflowState, string> = {
  loading: "加载中",
  empty: "暂无数据",
  degraded: "降级可用",
  error: "请求异常",
  ready: "已就绪",
};

type MetricItem = {
  label: string;
  value: string | number;
  note?: string;
};

type WorkbenchHeroProps = {
  eyebrow: string;
  title: string;
  description: string;
  metrics?: MetricItem[];
  meta?: string[];
};

export function WorkbenchHero({
  eyebrow,
  title,
  description,
  metrics = [],
  meta = [],
}: WorkbenchHeroProps) {
  return (
    <section className="workbench-hero">
      <div className="workbench-hero-main">
        <div className="eyebrow">{eyebrow}</div>
        <h1 className="hero-title">{title}</h1>
        <p className="hero-copy">{description}</p>
      </div>
      {metrics.length || meta.length ? (
        <aside className="workbench-hero-aside" aria-label={`${title} 状态`}>
          {metrics.length ? (
            <div className="metric-grid compact">
              {metrics.map((metric) => (
                <MetricTile
                  key={`${metric.label}-${metric.value}`}
                  label={metric.label}
                  note={metric.note}
                  value={metric.value}
                />
              ))}
            </div>
          ) : null}
          {meta.length ? (
            <div className="meta-strip">
              {meta.map((item) => (
                <span className="meta-chip" key={item}>
                  {item}
                </span>
              ))}
            </div>
          ) : null}
        </aside>
      ) : null}
    </section>
  );
}

export function WorkbenchSection({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
          <h2 className="panel-title">{title}</h2>
          {description ? <p className="panel-subtitle">{description}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

export function MetricTile({ label, value, note }: MetricItem) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <div className="metric-value">{value}</div>
      {note ? <div className="metric-note">{note}</div> : null}
    </div>
  );
}

export function StateSurface({
  state,
  title,
  detail,
}: {
  state: WorkflowState;
  title: string;
  detail?: string;
}) {
  return (
    <div className="state-surface" data-state={state}>
      <span className="state-kicker">{STATE_LABELS[state]}</span>
      <strong>{title}</strong>
      {detail ? <p>{detail}</p> : null}
    </div>
  );
}

export function MetadataState({ metadata }: { metadata?: CapabilityMetadata }) {
  if (!metadata) {
    return null;
  }

  if (metadata.degraded) {
    return (
      <StateSurface
        state="degraded"
        title="后端返回降级结果。"
        detail={[
          metadata.warnings?.join("; "),
          metadata.unavailableInputs?.length
            ? `不可用输入：${metadata.unavailableInputs.join(", ")}`
            : "",
        ]
          .filter(Boolean)
          .join(" ")}
      />
    );
  }

  return (
    <StateSurface
      state="ready"
      title="后端响应已就绪。"
      detail={`来源：${displayText(metadata.source, "后端服务")}`}
    />
  );
}
