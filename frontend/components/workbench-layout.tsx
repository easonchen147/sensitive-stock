import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

/* ─── Hero Banner ─── */

interface MetricItem {
  label: string;
  value: string | number;
  note?: string;
}

interface WorkbenchHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  metrics?: MetricItem[];
  meta?: string[];
}

export function WorkbenchHero({ eyebrow, title, description, metrics, meta }: WorkbenchHeroProps) {
  return (
    <div className="mb-8 grid gap-6 border-b border-border pb-6 lg:grid-cols-[1.35fr_0.65fr]">
      <div className="min-w-0">
        <span className="text-xs font-bold uppercase tracking-wider text-primary">{eyebrow}</span>
        <h1 className="mt-2 font-display text-3xl font-bold leading-tight tracking-tight text-foreground lg:text-4xl">
          {title}
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">{description}</p>
        {meta?.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {meta.map((item) => (
              <Badge key={item} variant="secondary" className="text-xs">
                {item}
              </Badge>
            ))}
          </div>
        ) : null}
      </div>

      {metrics?.length ? (
        <div className="grid content-start gap-3 rounded-lg border border-border bg-muted/50 p-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="grid gap-1">
              <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">
                {metric.label}
              </span>
              <span className="font-display text-2xl font-bold text-foreground">{metric.value}</span>
              {metric.note ? (
                <span className="text-xs text-muted-foreground">{metric.note}</span>
              ) : null}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

/* ─── Section Wrapper ─── */

interface WorkbenchSectionProps {
  eyebrow: string;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

export function WorkbenchSection({ eyebrow, title, subtitle, children, className }: WorkbenchSectionProps) {
  return (
    <Card className={cn("gap-0", className)}>
      <CardHeader className="pb-4">
        <span className="text-xs font-bold uppercase tracking-wider text-primary">{eyebrow}</span>
        <CardTitle className="font-display text-xl">{title}</CardTitle>
        {subtitle ? (
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        ) : null}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

/* ─── Metric Tile ─── */

interface MetricTileProps {
  label: string;
  value: string | number;
  note?: string;
}

export function MetricTile({ label, value, note }: MetricTileProps) {
  return (
    <div className="grid gap-1 rounded-lg border border-border bg-card p-3">
      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">{label}</span>
      <span className="font-display text-xl font-bold text-foreground">{value}</span>
      {note ? <span className="text-xs text-muted-foreground">{note}</span> : null}
    </div>
  );
}

/* ─── State Surface ─── */

type SurfaceState = "loading" | "empty" | "degraded" | "error" | "ready";

interface StateSurfaceProps {
  state: SurfaceState;
  title: string;
  detail?: string;
}

export function StateSurface({ state, title, detail }: StateSurfaceProps) {
  if (state === "loading") {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-border bg-muted/50 p-4">
        <Loader2 className="size-4 animate-spin text-primary" />
        <div className="grid gap-1">
          <span className="text-xs font-bold uppercase tracking-wider text-primary">加载中</span>
          <p className="text-sm text-muted-foreground">{title}</p>
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <Alert variant="destructive">
        <AlertCircle className="size-4" />
        <AlertTitle>错误</AlertTitle>
        <AlertDescription>{detail || title}</AlertDescription>
      </Alert>
    );
  }

  if (state === "degraded") {
    return (
      <Alert variant="destructive" className="border-warning/25 bg-warning-soft text-warning">
        <AlertCircle className="size-4" />
        <AlertTitle>降级</AlertTitle>
        <AlertDescription>{detail || title}</AlertDescription>
      </Alert>
    );
  }

  if (state === "ready") {
    return (
      <Alert className="border-positive/25 bg-positive-soft text-positive">
        <CheckCircle2 className="size-4" />
        <AlertTitle>就绪</AlertTitle>
        <AlertDescription>{title}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="rounded-lg border border-dashed border-border bg-muted/30 p-6 text-center">
      <p className="text-sm text-muted-foreground">{title}</p>
      {detail ? <p className="mt-1 text-xs text-muted-foreground">{detail}</p> : null}
    </div>
  );
}

/* ─── Metadata State ─── */

interface MetadataStateProps {
  metadata?: {
    source?: string;
    degraded?: boolean;
    fallback?: string;
  };
}

export function MetadataState({ metadata }: MetadataStateProps) {
  if (!metadata) return null;

  if (metadata.degraded) {
    return (
      <StateSurface
        state="degraded"
        title={`数据源降级：${metadata.source || "未知"}`}
        detail={metadata.fallback ? `备用源：${metadata.fallback}` : undefined}
      />
    );
  }

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <CheckCircle2 className="size-3 text-positive" />
      <span>数据源：{metadata.source || "akshare"}</span>
    </div>
  );
}
