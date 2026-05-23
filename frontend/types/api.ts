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

export type BacktestFillPolicy = {
  priceBasis: "open" | "close";
  barOffset: 0 | 1;
  temporal: "same_cycle" | "next_event";
};

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
  engine?: "akquant";
  engineVersion?: string;
  fillPolicy?: BacktestFillPolicy;
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

export type BacktestPresetExecutionMetadata = {
  engine: "akquant";
  engineVersion: string;
  runtimeAdapter: string;
  supportedModes: ExecutionMode[];
  fillPolicies: Array<BacktestFillPolicy & { mode: ExecutionMode }>;
  supportsRiskControls: boolean;
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
  executionMetadata?: BacktestPresetExecutionMetadata;
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
  degraded?: boolean;
  warnings?: string[];
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
  degraded?: boolean;
  warnings?: string[];
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
  primarySource?: string;
  fallbackSources?: string[];
  requestedLimit: number;
  degraded: boolean;
  warnings?: string[];
  channels?: MarketNewsChannel[];
  sourceCount?: number;
  sourceQuality?: MarketNewsSourceQuality;
  dedupeMetadata?: MarketNewsDedupeMetadata;
  items: MarketNewsItem[];
};

export type MarketNewsChannel = {
  name: string;
  source: string;
  status: "ok" | "degraded" | "failed";
  itemCount: number;
  warnings?: string[];
};

export type MarketNewsSourceQuality = {
  queriedChannels: number;
  succeededChannels: number;
  degradedChannels: number;
  failedChannels: number;
  totalItems: number;
  uniqueItems: number;
  duplicateItems: number;
  sourceCoverage: string[];
  qualityScore?: number;
  coverageScore?: number;
  freshnessScore?: number;
  reliabilityScore?: number;
  duplicatePressure?: number;
  qualityNotes?: string[];
};

export type MarketNewsDedupeMetadata = {
  strategy: string;
  originalCount: number;
  uniqueCount: number;
  duplicateCount: number;
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

export type MarketPredictionMetadata = {
  provider: string;
  model: string;
  requestMode?: "remote" | "heuristic";
  degraded: boolean;
  cached: boolean;
  schemaVersion: string;
  cacheKey: string;
  inputDigest: string;
  thinkingType?: "enabled" | "disabled";
  reasoningEffort?: "high" | "max";
  newsItemCount: number;
  keywordCount: number;
  sectorHintCount: number;
  symbolCount: number;
  latencyMs?: number;
  warnings?: string[];
};

export type MarketPrediction = {
  predictionId?: string;
  targetType: string;
  target: string;
  direction: "bullish" | "neutral" | "bearish";
  confidence: number;
  score: number;
  horizon: string;
  drivers: string[];
  sourceIds: string[];
};

export type MarketPredictionBacktestHandoff = {
  endpoint: string;
  suggestedPreset: string;
  symbols: string[];
  defaultParams: Record<string, unknown>;
  notes?: string[];
};

export type MarketNewsPredictionsResponse = MarketNewsIntelligenceResponse & {
  runId?: string;
  createdAt?: string;
  predictionMetadata: MarketPredictionMetadata;
  predictions: MarketPrediction[];
  predictionSummary?: string;
  riskNotes: string[];
  backtestHandoff: MarketPredictionBacktestHandoff;
};

export type MarketPredictionHistoryRun = {
  runId: string;
  createdAt: string;
  provider?: string;
  model?: string;
  thinkingType?: string;
  reasoningEffort?: string;
  degraded: boolean;
  predictionCount: number;
  qualityScore?: number;
  summary?: string;
};

export type MarketPredictionHistoryResponse = {
  items: MarketPredictionHistoryRun[];
  metadata: CapabilityMetadata;
};

export type MarketPredictionDetailResponse = MarketNewsPredictionsResponse & {
  runId: string;
  createdAt: string;
};

export type MarketPredictionEvaluationStatus = "hit" | "miss" | "neutral" | "pending";

export type MarketPredictionEvaluationSummary = {
  total: number;
  assessable: number;
  hit: number;
  miss: number;
  neutral: number;
  pending: number;
  hitRate?: number | null;
};

export type MarketPredictionEvaluationItem = {
  predictionId: string;
  target: string;
  direction: "bullish" | "neutral" | "bearish";
  status: MarketPredictionEvaluationStatus;
  actualChangePercent?: number | null;
  note: string;
};

export type MarketPredictionEvaluationResponse = {
  runId: string;
  evaluatedAt: string;
  evaluationSummary: MarketPredictionEvaluationSummary;
  evaluationItems: MarketPredictionEvaluationItem[];
  metadata: CapabilityMetadata;
};

export type CapabilityMetadata = {
  source: string;
  degraded: boolean;
  warnings?: string[];
  unavailableInputs?: string[];
  [key: string]: unknown;
};

export type ScreenerFilters = {
  minPrice?: number;
  maxPrice?: number;
  minChangePercent?: number;
  maxChangePercent?: number;
  sectors?: string[];
};

export type ScreenerRunPayload = {
  universe: string[];
  prompt?: string;
  filters: ScreenerFilters;
  sortBy?: "score" | "price" | "changePercent";
  limit?: number;
  backtestStartDate?: string;
  backtestEndDate?: string;
};

export type ScreenerCandidate = {
  symbol: string;
  name: string;
  price: number;
  changePercent: number;
  score: number;
  matchedRules: string[];
  factorSummary: Record<string, number>;
};

export type ScreenerRunResponse = {
  items: ScreenerCandidate[];
  summary: Record<string, unknown>;
  appliedFilters: ScreenerFilters;
  interpretedPrompt: string;
  exportRows: Array<Record<string, unknown>>;
  backtestHandoff: {
    endpoint: string;
    payload: BacktestRunPayload;
  };
  metadata: CapabilityMetadata;
};

export type ScreenerOverviewResponse = {
  status: "migrated";
  templates: Array<Record<string, unknown>>;
  metadata: CapabilityMetadata;
};

export type ScreenerExportResponse = {
  format: "json" | "csv";
  columns: string[];
  rows: Array<Record<string, unknown>>;
  metadata: CapabilityMetadata;
};

export type DiagnosisPayload = {
  symbol: string;
  startDate: string;
  endDate: string;
  includeNews?: boolean;
};

export type DiagnosisSection = {
  title: string;
  tone: "positive" | "neutral" | "warning";
  summary: string;
};

export type DiagnosisResponse = {
  symbol: string;
  name: string;
  marketContext: Record<string, unknown>;
  indicators: Array<Record<string, unknown>>;
  sections: DiagnosisSection[];
  riskNotes: string[];
  metadata: CapabilityMetadata;
};

export type FactorAnalysisPayload = {
  symbol: string;
  startDate: string;
  endDate: string;
  factors?: string[];
  forwardDays?: number;
  topN?: number;
};

export type FactorAnalysisResponse = {
  symbol: string;
  window: Record<string, unknown>;
  latestFactors: Record<string, number>;
  rankedFactors: Array<{ name: string; ic: number; absIc: number }>;
  summary: Record<string, unknown>;
  metadata: CapabilityMetadata;
};

export type PortfolioOptimizationPayload = {
  symbols: string[];
  startDate: string;
  endDate: string;
  objective: "equal_weight" | "minimum_variance" | "maximum_sharpe" | "risk_parity";
  riskFreeRate?: number;
};

export type PortfolioOptimizationResponse = {
  objective: string;
  window: Record<string, unknown>;
  allocations: Array<{ symbol: string; weight: number }>;
  statistics: Record<string, number>;
  metadata: CapabilityMetadata;
};
