export type CapabilityStatus = "migrated" | "skeleton" | "planned";

export type Capability = {
  name: string;
  label: string;
  status: CapabilityStatus;
  path: string;
  summary: string;
};

export type CapabilitiesResponse = {
  items: Capability[];
};

export type AuthUser = {
  username: string;
  role: string;
  scope: string;
};

export type AuthLoginRequest = {
  username: string;
  password: string;
};

export type AuthSession = {
  authenticated: boolean;
  expiresIn: number;
  user: AuthUser;
};

export type AuthLoginResponse = {
  accessToken: string;
  tokenType: "Bearer";
  expiresIn: number;
  user: AuthUser;
};

export type StrategyMode = "preset" | "custom";
export type ExecutionMode = "close" | "next_open";

export type BacktestSeriesPoint = {
  date: string;
  value: number;
};

export type BacktestMonthlyReturn = {
  month: string;
  value: number;
};

export type BacktestTrade = {
  date: string;
  action: string;
  reason: string;
  price: number;
  shares: number;
  notional: number;
  fee: number;
  tax: number;
};

export type BacktestComparison = {
  benchmark_total_return?: number | null;
  excess_return?: number | null;
  information_ratio?: number | null;
  tracking_error?: number | null;
};

export type BacktestTradeStats = {
  tradeCount: number;
  winRate: number;
  averageHoldingDays: number;
  averageTradeReturn: number;
  totalCosts: number;
  turnover: number;
  endingEquity?: number;
  netProfit?: number;
  exposureRate?: number;
};

export type BacktestAssumption = {
  label: string;
  value: string;
  detail: string;
};

export type BacktestInsight = {
  title: string;
  tone: "positive" | "neutral" | "warning";
  detail: string;
};

export type BacktestSettings = {
  symbol: string;
  benchmarkSymbol?: string | null;
  adjust: "" | "qfq" | "hfq";
  strategyMode: StrategyMode;
  strategyPreset?: string | null;
  strategyLabel: string;
  executionMode: ExecutionMode;
  positionSize: number;
  lotSize: number;
  tradingFee: number;
  stampTax: number;
  slippage: number;
  stopLoss: number;
  takeProfit: number;
  initialCapital?: number;
  primarySource?: string;
  fallbackSources?: string[];
};

export type BacktestSeries = {
  equity: BacktestSeriesPoint[];
  benchmark: BacktestSeriesPoint[];
  drawdown: BacktestSeriesPoint[];
  position: BacktestSeriesPoint[];
  cash: BacktestSeriesPoint[];
  monthlyReturns: BacktestMonthlyReturn[];
};

export type BacktestSymbolResult = {
  symbol: string;
  settings: BacktestSettings;
  metrics: Record<string, number>;
  comparison: BacktestComparison;
  series: BacktestSeries;
  tradeStats: BacktestTradeStats;
  trades: BacktestTrade[];
  warnings: string[];
  assumptions: BacktestAssumption[];
  insights: BacktestInsight[];
};

export type BacktestFailure = {
  symbol: string;
  message: string;
};

export type BacktestMarketPayload = {
  symbols: string[];
  startDate: string;
  endDate: string;
  adjust: "" | "qfq" | "hfq";
  benchmarkSymbol?: string;
};

export type BacktestStrategyPayload = {
  mode: StrategyMode;
  presetId?: string;
  code: string;
  params: Record<string, unknown>;
};

export type BacktestExecutionPayload = {
  mode: ExecutionMode;
  positionSize: number;
  lotSize: number;
};

export type BacktestCostPayload = {
  tradingFee: number;
  stampTax: number;
  slippage: number;
};

export type BacktestRiskPayload = {
  stopLoss: number;
  takeProfit: number;
};

export type BacktestRunPayload = {
  market: BacktestMarketPayload;
  strategy: BacktestStrategyPayload;
  execution: BacktestExecutionPayload;
  costs: BacktestCostPayload;
  risk: BacktestRiskPayload;
  initialCapital: number;
};

export type BacktestRunResponse = {
  results: BacktestSymbolResult[];
  failures: BacktestFailure[];
};

export type BacktestPresetParameter = {
  name: string;
  label: string;
  type: "number" | "select" | "text";
  group?: string;
  helpText?: string;
  default: number | string;
  min?: number;
  max?: number;
  step?: number;
  options?: Array<{ label: string; value: string }>;
};

export type BacktestPreset = {
  id: string;
  label: string;
  description: string;
  summary: string;
  useCase: string;
  riskNotes: string;
  defaultParams: Record<string, unknown>;
  parameterSchema: BacktestPresetParameter[];
  code: string;
};

export type BacktestPresetsResponse = {
  items: BacktestPreset[];
};

export type MarketOverview = {
  primarySource?: string;
  fallbackSources?: string[];
  routes: Record<string, string>;
};

export type MarketQuote = {
  symbol: string;
  name?: string | null;
  price?: number | null;
  changePercent?: number | null;
  changeAmount?: number | null;
  volume?: number | null;
  amount?: number | null;
  open?: number | null;
  preClose?: number | null;
  high?: number | null;
  low?: number | null;
};

export type MarketQuotesResponse = {
  source: string;
  items: MarketQuote[];
};

export type MarketSector = {
  name: string;
  code?: string | null;
  type: string;
  changePercent?: number | null;
  leadingStock?: string | null;
  leadingStockChangePercent?: number | null;
  source: string;
};

export type MarketSectorsResponse = {
  source: string;
  sectorType: string;
  items: MarketSector[];
};

export type MarketNewsItem = {
  id: string;
  publishedAt: string;
  title: string;
  content: string;
  important: boolean;
  tags: string[];
  sourceUrl?: string;
  source: string;
};

export type MarketNewsResponse = {
  source: string;
  requestedLimit: number;
  degraded: boolean;
  items: MarketNewsItem[];
};

export type MarketKeyword = {
  keyword: string;
  count: number;
  coverage: number;
};

export type MarketSectorHint = {
  name: string;
  boardType: string;
  score: number;
  matchedKeywords: string[];
};

export type MarketNewsIntelligenceResponse = MarketNewsResponse & {
  keywords: MarketKeyword[];
  sectorHints: MarketSectorHint[];
};
