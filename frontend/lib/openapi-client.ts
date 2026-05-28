import { buildBackendProxyPath, buildLoginRedirectPath } from "@/lib/auth";
import type {
  BacktestPresetsResponse,
  BacktestRunPayload,
  BacktestRunResponse,
  CapabilitiesResponse,
  DiagnosisPayload,
  DiagnosisResponse,
  FactorAnalysisPayload,
  FactorAnalysisResponse,
  MarketNewsIntelligenceResponse,
  MarketPredictionDetailResponse,
  MarketPredictionEvaluationResponse,
  MarketPredictionHistoryResponse,
  MarketNewsPredictionsResponse,
  MarketNewsResponse,
  MarketOverview,
  MarketQuotesResponse,
  MarketSectorsResponse,
  PortfolioOptimizationPayload,
  PortfolioOptimizationResponse,
  ScreenerExportResponse,
  ScreenerOverviewResponse,
  ScreenerRunPayload,
  ScreenerRunResponse,
} from "@/types/api";

export const OPENAPI_ROUTE_BINDINGS = {
  openapiJson: { method: "GET", path: "/api/v1/openapi.json", public: true },
  health: { method: "GET", path: "/api/v1/health", public: true },
  authLogin: { method: "POST", path: "/api/v1/auth/login", public: true },
  authRegister: { method: "POST", path: "/api/v1/auth/register", public: true },
  authSession: { method: "GET", path: "/api/v1/auth/session", public: false },
  capabilities: { method: "GET", path: "/api/v1/capabilities", public: false },
  backtestPresets: { method: "GET", path: "/api/v1/backtests/presets", public: false },
  backtestRun: { method: "POST", path: "/api/v1/backtests/run", public: false },
  marketOverview: { method: "GET", path: "/api/v1/market", public: false },
  marketQuotes: { method: "GET", path: "/api/v1/market/quotes", public: false },
  marketSectors: { method: "GET", path: "/api/v1/market/sectors", public: false },
  marketNews: { method: "GET", path: "/api/v1/market/news", public: false },
  marketNewsIntelligence: {
    method: "GET",
    path: "/api/v1/market/news/intelligence",
    public: false,
  },
  marketNewsPredictions: {
    method: "GET",
    path: "/api/v1/market/news/predictions",
    public: false,
  },
  marketPredictionHistory: {
    method: "GET",
    path: "/api/v1/market/news/prediction-history",
    public: false,
  },
  marketPredictionDetail: {
    method: "GET",
    path: "/api/v1/market/news/predictions/{runId}",
    public: false,
  },
  marketPredictionEvaluation: {
    method: "GET",
    path: "/api/v1/market/news/predictions/{runId}/evaluate",
    public: false,
  },
  screenerOverview: { method: "GET", path: "/api/v1/screener", public: false },
  screenerRun: { method: "POST", path: "/api/v1/screener/run", public: false },
  screenerExport: { method: "POST", path: "/api/v1/screener/export", public: false },
  diagnosisOverview: { method: "GET", path: "/api/v1/diagnosis", public: false },
  diagnosisRun: { method: "POST", path: "/api/v1/diagnosis/run", public: false },
  factorsOverview: { method: "GET", path: "/api/v1/factors", public: false },
  factorsAnalyze: { method: "POST", path: "/api/v1/factors/analyze", public: false },
  portfolioOverview: { method: "GET", path: "/api/v1/portfolio", public: false },
  portfolioOptimize: { method: "POST", path: "/api/v1/portfolio/optimize", public: false },
  stockCompare: { method: "GET", path: "/api/v1/market/compare", public: false },
  stockDetail: { method: "GET", path: "/api/v1/market/stock/{symbol}/detail", public: false },
  stockKline: { method: "GET", path: "/api/v1/market/stock/{symbol}/kline", public: false },
  stockFinancials: { method: "GET", path: "/api/v1/market/stock/{symbol}/financials", public: false },
  stockNews: { method: "GET", path: "/api/v1/market/stock/{symbol}/news", public: false },
  newsCategories: { method: "GET", path: "/api/v1/market/news/categories", public: false },
  generateStrategy: { method: "POST", path: "/api/v1/backtests/generate-strategy", public: false },
  stockQA: { method: "POST", path: "/api/v1/qa/ask", public: false },
  dailyRun: { method: "POST", path: "/api/v1/daily/run", public: false },
  dailyLatest: { method: "GET", path: "/api/v1/daily/latest", public: false },
  dailyHistory: { method: "GET", path: "/api/v1/daily/history", public: false },
  watchlistList: { method: "GET", path: "/api/v1/watchlist", public: false },
  watchlistAdd: { method: "POST", path: "/api/v1/watchlist", public: false },
  watchlistUpdate: { method: "PUT", path: "/api/v1/watchlist/{symbol}", public: false },
  watchlistRemove: { method: "DELETE", path: "/api/v1/watchlist/{symbol}", public: false },
} as const;

export type OpenApiRouteKey = keyof typeof OPENAPI_ROUTE_BINDINGS;

export type OpenApiRouteResponseMap = {
  capabilities: CapabilitiesResponse;
  backtestPresets: BacktestPresetsResponse;
  backtestRun: BacktestRunResponse;
  marketOverview: MarketOverview;
  marketQuotes: MarketQuotesResponse;
  marketSectors: MarketSectorsResponse;
  marketNews: MarketNewsResponse;
  marketNewsIntelligence: MarketNewsIntelligenceResponse;
  marketNewsPredictions: MarketNewsPredictionsResponse;
  marketPredictionHistory: MarketPredictionHistoryResponse;
  marketPredictionDetail: MarketPredictionDetailResponse;
  marketPredictionEvaluation: MarketPredictionEvaluationResponse;
  screenerOverview: ScreenerOverviewResponse;
  screenerRun: ScreenerRunResponse;
  screenerExport: ScreenerExportResponse;
  diagnosisRun: DiagnosisResponse;
  factorsAnalyze: FactorAnalysisResponse;
  portfolioOptimize: PortfolioOptimizationResponse;
  stockCompare: import("@/types/api").StockCompareResponse;
  stockDetail: import("@/types/api").StockDetail;
  stockKline: import("@/types/api").KlineResponse;
  stockFinancials: import("@/types/api").FinancialSummaryResponse;
  stockNews: import("@/types/api").StockNewsResponse;
  newsCategories: import("@/types/api").NewsCategoriesResponse;
  generateStrategy: import("@/types/api").StrategyGenerateResponse;
  stockQA: import("@/types/api").StockQAResponse;
  dailyRun: import("@/types/api").DailyReport;
  dailyLatest: import("@/types/api").DailyReport;
  dailyHistory: import("@/types/api").DailyHistoryResponse;
  watchlistList: import("@/types/api").WatchlistResponse;
  watchlistAdd: import("@/types/api").WatchlistItem;
  watchlistUpdate: import("@/types/api").WatchlistItem;
  watchlistRemove: import("@/types/api").OkResponse;
};

export type OpenApiRouteRequestMap = {
  backtestRun: BacktestRunPayload;
  screenerRun: ScreenerRunPayload;
  screenerExport: ScreenerRunPayload & { format?: "json" | "csv" };
  diagnosisRun: DiagnosisPayload;
  factorsAnalyze: FactorAnalysisPayload;
  portfolioOptimize: PortfolioOptimizationPayload;
  generateStrategy: import("@/types/api").StrategyGeneratePayload;
  stockQA: import("@/types/api").StockQAPayload;
  dailyRun: import("@/types/api").DailyRunPayload;
  watchlistAdd: import("@/types/api").WatchlistAddPayload;
  watchlistUpdate: import("@/types/api").WatchlistUpdatePayload;
};

type QueryValue = string | number | boolean | null | undefined;

type FetchOpenApiRouteOptions<K extends keyof OpenApiRouteResponseMap> = {
  body?: K extends keyof OpenApiRouteRequestMap ? OpenApiRouteRequestMap[K] : never;
  pathParams?: Record<string, string>;
  query?: Record<string, QueryValue>;
  init?: RequestInit;
};

export function getOpenApiBinding(key: OpenApiRouteKey) {
  return OPENAPI_ROUTE_BINDINGS[key];
}

export function findOpenApiRouteByPath(path: string) {
  return Object.entries(OPENAPI_ROUTE_BINDINGS).find(
    ([, binding]) => binding.path === path || matchesOpenApiTemplate(binding.path, path),
  ) || null;
}

export function isProtectedOpenApiPath(path: string): boolean {
  const route = findOpenApiRouteByPath(path);
  return Boolean(route && !route[1].public);
}

export function buildOpenApiPath(
  key: OpenApiRouteKey,
  query?: Record<string, QueryValue>,
  pathParams?: Record<string, string>,
): string {
  const binding = getOpenApiBinding(key);
  const resolvedPath = binding.path.replace(/\{([^}]+)\}/g, (_, name: string) => {
    const value = pathParams?.[name];
    if (!value) {
      throw new Error(`Missing path parameter: ${name}`);
    }
    return encodeURIComponent(value);
  });
  const search = new URLSearchParams();

  Object.entries(query || {}).forEach(([queryKey, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      search.set(queryKey, String(value));
    }
  });

  const queryString = search.toString();
  return queryString ? `${resolvedPath}?${queryString}` : resolvedPath;
}

export function buildOpenApiProxyPath(
  key: OpenApiRouteKey,
  query?: Record<string, QueryValue>,
  pathParams?: Record<string, string>,
): string {
  return buildBackendProxyPath(buildOpenApiPath(key, query, pathParams));
}

export async function fetchOpenApiRoute<K extends keyof OpenApiRouteResponseMap>(
  key: K,
  options: FetchOpenApiRouteOptions<K> = {},
): Promise<OpenApiRouteResponseMap[K]> {
  const binding = getOpenApiBinding(key);
  const headers = new Headers(options.init?.headers);
  const init: RequestInit = {
    cache: "no-store",
    ...options.init,
    method: options.init?.method || binding.method,
    headers,
  };

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
    init.body = JSON.stringify(options.body);
  }

  const response = await fetch(
    buildOpenApiProxyPath(key, options.query, options.pathParams),
    init,
  );
  const responseBody = await response.json().catch(() => null);

  if (response.status === 401 && typeof window !== "undefined") {
    window.location.assign(buildLoginRedirectPath(window.location.pathname));
    throw new Error("需要登录后继续。");
  }

  if (!response.ok) {
    throw new Error(
      responseBody?.error?.message ||
        `${binding.path} 请求失败，状态码 ${response.status}`,
    );
  }

  return responseBody as OpenApiRouteResponseMap[K];
}

function matchesOpenApiTemplate(template: string, path: string): boolean {
  if (!template.includes("{")) {
    return false;
  }
  const pattern = template
    .split("/")
    .map((part) => (part.startsWith("{") && part.endsWith("}") ? "[^/]+" : escapeRegex(part)))
    .join("/");
  return new RegExp(`^${pattern}$`).test(path);
}

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
