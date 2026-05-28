import type {
  AuthLoginRequest,
  AuthLoginResponse,
  AuthSession,
  BacktestPreset,
  BacktestRunPayload,
  BacktestRunResponse,
  Capability,
  DailyHistoryResponse,
  DailyReport,
  DailyRunPayload,
  MarketNewsIntelligenceResponse,
  MarketPredictionDetailResponse,
  MarketPredictionEvaluationResponse,
  MarketPredictionHistoryResponse,
  MarketNewsPredictionsResponse,
  MarketNewsResponse,
  MarketOverview,
  MarketQuotesResponse,
  MarketSectorsResponse,
  DiagnosisPayload,
  DiagnosisResponse,
  FactorAnalysisPayload,
  FactorAnalysisResponse,
  PortfolioOptimizationPayload,
  PortfolioOptimizationResponse,
  ScreenerExportResponse,
  ScreenerOverviewResponse,
  ScreenerRunPayload,
  ScreenerRunResponse,
} from "@/types/api";
import { fetchOpenApiRoute } from "@/lib/openapi-client";

async function fetchAuthJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    cache: "no-store",
    ...init,
  });
  const responseBody = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      responseBody?.error?.message || `${path} 请求失败，状态码 ${response.status}`,
    );
  }

  return responseBody as T;
}

export async function getCapabilities(): Promise<Capability[]> {
  try {
    const payload = await fetchOpenApiRoute("capabilities");
    return payload.items;
  } catch {
    return [
      {
        name: "backtest",
        label: "股票回测",
        status: "ready",
        path: "/api/v1/backtests/run",
        summary: "回测主链路可调用，支持策略、成本、风控和结构化结果。",
      },
      {
        name: "market",
        label: "行情中心",
        status: "ready",
        path: "/api/v1/market",
        summary: "行情、资讯、情报、预测历史、详情和评估接口可调用。",
      },
      {
        name: "diagnosis",
        label: "智能诊股",
        status: "ready",
        path: "/api/v1/diagnosis/run",
        summary: "诊股接口可调用，返回行情上下文、指标摘要和风险提示。",
      },
      {
        name: "screener",
        label: "条件选股",
        status: "ready",
        path: "/api/v1/screener/run",
        summary: "结构化筛选、结果导出与回测交接接口可调用。",
      },
      {
        name: "factors",
        label: "因子分析",
        status: "ready",
        path: "/api/v1/factors/analyze",
        summary: "因子快照、相关性排名和分析窗口接口可调用。",
      },
      {
        name: "portfolio",
        label: "组合优化",
        status: "ready",
        path: "/api/v1/portfolio/optimize",
        summary: "组合优化目标、目标权重和统计指标接口可调用。",
      },
      {
        name: "qa",
        label: "AI 问答",
        status: "ready",
        path: "/api/v1/qa/ask",
        summary: "输入股票代码和自然语言问题，获取 AI 驱动的分析和回答。",
      },
      {
        name: "daily",
        label: "每日复盘",
        status: "ready",
        path: "/api/v1/daily/run",
        summary: "AI 驱动的每日市场分析，包括精选推荐、板块分析和风险提示。",
      },
    ];
  }
}

export async function runBacktests(payload: BacktestRunPayload): Promise<BacktestRunResponse> {
  return fetchOpenApiRoute("backtestRun", { body: payload });
}

const FALLBACK_PRESETS: BacktestPreset[] = [
  {
    id: "ma_cross",
    label: "双均线策略",
    description: "由回测适配器执行的双均线交叉预设。",
    summary: "用快慢均线交叉寻找趋势启动与结束区间。",
    useCase: "适合做趋势方向研究和参数敏感性检查。",
    riskNotes: "震荡市场里容易出现频繁反复开平仓。",
    defaultParams: {
      fast_window: 5,
      slow_window: 20,
    },
    executionMetadata: {
      engine: "akquant",
      engineVersion: "0.2.37",
      runtimeAdapter: "signal_replay",
      supportedModes: ["close", "next_open"],
      fillPolicies: [
        {
          mode: "close",
          priceBasis: "close",
          barOffset: 0,
          temporal: "same_cycle",
        },
        {
          mode: "next_open",
          priceBasis: "open",
          barOffset: 1,
          temporal: "same_cycle",
        },
      ],
      supportsRiskControls: true,
      supportsVolumeLimit: true,
      supportsMinCommission: true,
      supportsTransferFee: true,
      strategyRiskId: "signal_replay",
      supportedSlippageTypes: ["zero", "percent", "fixed", "ticks"],
    },
    parameterSchema: [
      {
        name: "fast_window",
        label: "快线窗口",
        type: "number",
        group: "trend",
        helpText: "更短的窗口会更敏感，也更容易产生噪声。",
        default: 5,
        min: 2,
        max: 60,
        step: 1,
      },
      {
        name: "slow_window",
        label: "慢线窗口",
        type: "number",
        group: "trend",
        helpText: "更长的窗口更稳定，但确认趋势更慢。",
        default: 20,
        min: 5,
        max: 120,
        step: 1,
      },
    ],
    code: `def generate_signals(data, ctx):
    fast_window = int(ctx.params.get("fast_window", 5))
    slow_window = int(ctx.params.get("slow_window", 20))

    close = data["close"]
    fast = ctx.sma(close, fast_window)
    slow = ctx.sma(close, slow_window)

    signal = ctx.new_signal()
    signal[ctx.cross_over(fast, slow)] = 1
    signal[ctx.cross_under(fast, slow)] = 0
    return signal.ffill().fillna(0)
`,
  },
];

export async function getBacktestPresets(): Promise<BacktestPreset[]> {
  try {
    const payload = await fetchOpenApiRoute("backtestPresets");
    return payload.items;
  } catch {
    return FALLBACK_PRESETS;
  }
}

export async function getMarketOverview(): Promise<MarketOverview> {
  return fetchOpenApiRoute("marketOverview");
}

export async function getMarketQuotes(symbols: string[]): Promise<MarketQuotesResponse> {
  return fetchOpenApiRoute("marketQuotes", { query: { symbols: symbols.join(",") } });
}

export async function getMarketSectors(
  sectorType: "concept" | "industry",
  limit = 8,
): Promise<MarketSectorsResponse> {
  return fetchOpenApiRoute("marketSectors", { query: { sectorType, limit } });
}

export async function getMarketNews(limit = 12): Promise<MarketNewsResponse> {
  return fetchOpenApiRoute("marketNews", { query: { limit } });
}

export async function getMarketNewsIntelligence(
  limit = 60,
): Promise<MarketNewsIntelligenceResponse> {
  return fetchOpenApiRoute("marketNewsIntelligence", { query: { limit } });
}

export async function getMarketNewsPredictions(
  limit = 60,
  symbols: string[] = [],
  options: { thinking?: "enabled" | "disabled"; reasoningEffort?: "high" | "max" } = {},
): Promise<MarketNewsPredictionsResponse> {
  return fetchOpenApiRoute("marketNewsPredictions", {
    query: {
      limit,
      symbols: symbols.join(","),
      thinking: options.thinking,
      reasoningEffort: options.reasoningEffort,
    },
  });
}

export async function getMarketPredictionHistory(
  limit = 12,
): Promise<MarketPredictionHistoryResponse> {
  return fetchOpenApiRoute("marketPredictionHistory", { query: { limit } });
}

export async function getMarketPredictionDetail(
  runId: string,
): Promise<MarketPredictionDetailResponse> {
  return fetchOpenApiRoute("marketPredictionDetail", { pathParams: { runId } });
}

export async function evaluateMarketPredictionRun(
  runId: string,
): Promise<MarketPredictionEvaluationResponse> {
  return fetchOpenApiRoute("marketPredictionEvaluation", { pathParams: { runId } });
}

export async function getScreenerOverview(): Promise<ScreenerOverviewResponse> {
  return fetchOpenApiRoute("screenerOverview");
}

export async function runScreener(payload: ScreenerRunPayload): Promise<ScreenerRunResponse> {
  return fetchOpenApiRoute("screenerRun", { body: payload });
}

export async function exportScreener(payload: ScreenerRunPayload): Promise<ScreenerExportResponse> {
  return fetchOpenApiRoute("screenerExport", { body: { ...payload, format: "json" } });
}

export async function runDiagnosis(payload: DiagnosisPayload): Promise<DiagnosisResponse> {
  return fetchOpenApiRoute("diagnosisRun", { body: payload });
}

export async function analyzeFactors(
  payload: FactorAnalysisPayload,
): Promise<FactorAnalysisResponse> {
  return fetchOpenApiRoute("factorsAnalyze", { body: payload });
}

export async function optimizePortfolio(
  payload: PortfolioOptimizationPayload,
): Promise<PortfolioOptimizationResponse> {
  return fetchOpenApiRoute("portfolioOptimize", { body: payload });
}

export async function login(payload: AuthLoginRequest): Promise<AuthLoginResponse> {
  return fetchAuthJson<AuthLoginResponse>("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function getSession(): Promise<AuthSession> {
  return fetchAuthJson<AuthSession>("/api/auth/session");
}

export async function logout(): Promise<void> {
  await fetchAuthJson<{ ok: boolean }>("/api/auth/logout", {
    method: "POST",
  });
}

// --- New API functions for Phase 1 ---

export async function getStockCompare(symbols: string[]): Promise<import("@/types/api").StockCompareResponse> {
  return fetchOpenApiRoute("stockCompare" as any, { query: { symbols: symbols.join(",") } });
}

export async function getStockDetail(symbol: string): Promise<import("@/types/api").StockDetail> {
  return fetchOpenApiRoute("stockDetail" as any, { pathParams: { symbol } });
}

export async function getKlineData(
  symbol: string,
  period: string = "daily",
  startDate?: string,
  endDate?: string,
): Promise<import("@/types/api").KlineResponse> {
  const query: Record<string, string> = { period };
  if (startDate) query.startDate = startDate;
  if (endDate) query.endDate = endDate;
  return fetchOpenApiRoute("stockKline" as any, { pathParams: { symbol }, query });
}

export async function getFinancialSummary(symbol: string): Promise<import("@/types/api").FinancialSummaryResponse> {
  return fetchOpenApiRoute("stockFinancials" as any, { pathParams: { symbol } });
}

export async function getStockNews(symbol: string, limit = 10): Promise<import("@/types/api").StockNewsResponse> {
  return fetchOpenApiRoute("stockNews" as any, { pathParams: { symbol }, query: { limit } });
}

export async function getNewsCategories(): Promise<import("@/types/api").NewsCategoriesResponse> {
  return fetchOpenApiRoute("newsCategories" as any);
}

export async function generateStrategy(description: string): Promise<import("@/types/api").StrategyGenerateResponse> {
  return fetchOpenApiRoute("generateStrategy" as any, { body: { description } });
}

export async function askStockQuestion(question: string, symbols: string[] = []): Promise<import("@/types/api").StockQAResponse> {
  return fetchOpenApiRoute("stockQA" as any, { body: { question, symbols } });
}

export async function runDailyAnalysis(universe?: string[]): Promise<DailyReport> {
  return fetchOpenApiRoute("dailyRun" as any, { body: { universe } });
}

export async function getLatestDailyReport(): Promise<DailyReport> {
  return fetchOpenApiRoute("dailyLatest" as any);
}

export async function getDailyHistory(limit = 10): Promise<DailyHistoryResponse> {
  return fetchOpenApiRoute("dailyHistory" as any, { query: { limit } });
}

export async function registerUser(payload: import("@/types/api").RegisterPayload): Promise<AuthLoginResponse> {
  return fetchOpenApiRoute("authRegister" as any, { body: payload });
}

export async function getWatchlist(): Promise<import("@/types/api").WatchlistResponse> {
  return fetchOpenApiRoute("watchlistList" as any);
}

export async function addToWatchlist(payload: import("@/types/api").WatchlistAddPayload): Promise<import("@/types/api").WatchlistItem> {
  return fetchOpenApiRoute("watchlistAdd" as any, { body: payload });
}

export async function updateWatchlistItem(symbol: string, payload: import("@/types/api").WatchlistUpdatePayload): Promise<import("@/types/api").WatchlistItem> {
  return fetchOpenApiRoute("watchlistUpdate" as any, { pathParams: { symbol }, body: payload });
}

export async function removeFromWatchlist(symbol: string): Promise<import("@/types/api").OkResponse> {
  return fetchOpenApiRoute("watchlistRemove" as any, { pathParams: { symbol } });
}
