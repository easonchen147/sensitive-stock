import type {
  CapabilityStatus,
  ExecutionMode,
  MarketPredictionEvaluationStatus,
  PortfolioOptimizationPayload,
} from "@/types/api";

export function displayText(value?: string | null, fallback = "暂无"): string {
  const normalized = String(value ?? "").trim();
  return normalized || fallback;
}

export function displayNumber(value?: number | null, digits = 2, fallback = "暂无"): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return fallback;
  }
  return value.toFixed(digits);
}

export function displayPercent(
  value?: number | null,
  digits = 2,
  fallback = "暂无",
): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return fallback;
  }
  return `${value.toFixed(digits)}%`;
}

export function displayRatioPercent(
  value?: number | null,
  digits = 2,
  fallback = "暂无",
): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return fallback;
  }
  return `${(value * 100).toFixed(digits)}%`;
}

export function displaySignedPercent(value?: number | null): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "暂无";
  }
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function displayCapabilityStatus(status: CapabilityStatus): string {
  const labels: Record<CapabilityStatus, string> = {
    ready: "可用",
    limited: "受限",
    disabled: "停用",
  };
  return labels[status] || status;
}

export function displayWorkflowStatus(status?: string | null): string {
  const labels: Record<string, string> = {
    limited: "受限",
    disabled: "停用",
    ok: "正常",
    degraded: "降级",
    failed: "失败",
    hit: "命中",
    miss: "未命中",
    neutral: "中性命中",
    pending: "待评估",
    ready: "已就绪",
    loading: "加载中",
    empty: "暂无数据",
    error: "请求异常",
    remote: "远程模型",
    heuristic: "本地启发式",
    local_heuristic: "本地启发式",
    deepseek: "深度求索模型",
    "keyword-sector-rules": "关键词板块规则",
    "deepseek-v4-flash": "深度求索快速模型",
    akquant: "量化回测引擎",
    AKQuant: "量化回测引擎",
    cached: "缓存结果",
    fresh: "实时生成",
  };
  return labels[String(status ?? "")] || displayText(status);
}

export function displayPredictionDirection(direction?: string | null): string {
  const labels: Record<string, string> = {
    bullish: "看多",
    neutral: "中性",
    bearish: "看空",
  };
  return labels[String(direction ?? "")] || displayText(direction);
}

export function displayEvaluationStatus(status: MarketPredictionEvaluationStatus): string {
  return displayWorkflowStatus(status);
}

export function displayThinkingType(value?: string | null): string {
  const labels: Record<string, string> = {
    enabled: "思考模式",
    disabled: "非思考模式",
  };
  return labels[String(value ?? "")] || displayText(value, "跟随后端默认");
}

export function displayReasoningEffort(value?: string | null): string {
  const labels: Record<string, string> = {
    high: "高",
    max: "最高",
  };
  return labels[String(value ?? "")] || displayText(value, "跟随后端默认");
}

export function displaySectorType(value: "concept" | "industry"): string {
  return value === "industry" ? "行业板块" : "概念板块";
}

export function displayExecutionMode(value: ExecutionMode): string {
  return value === "next_open" ? "次日开盘成交" : "当日收盘成交";
}

export function displayAdjustMode(value: "" | "qfq" | "hfq"): string {
  if (value === "qfq") {
    return "前复权";
  }
  if (value === "hfq") {
    return "后复权";
  }
  return "不复权";
}

export function displayStrategyMode(value: "preset" | "custom"): string {
  return value === "custom" ? "自定义策略" : "预设策略";
}

export function displayTradeAction(value?: string | null): string {
  const labels: Record<string, string> = {
    buy: "买入",
    sell: "卖出",
    hold: "持有",
  };
  return labels[String(value ?? "").toLowerCase()] || displayText(value);
}

export function displayTone(value?: string | null): string {
  const labels: Record<string, string> = {
    positive: "积极",
    neutral: "中性",
    warning: "警示",
  };
  return labels[String(value ?? "")] || displayText(value);
}

export function displayPortfolioObjective(value: PortfolioOptimizationPayload["objective"] | string): string {
  const labels: Record<string, string> = {
    equal_weight: "等权配置",
    minimum_variance: "最小方差",
    maximum_sharpe: "最大夏普",
    risk_parity: "风险平价",
  };
  return labels[String(value)] || displayText(value);
}
