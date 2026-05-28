"use client";

import { useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

import {
  evaluateMarketPredictionRun,
  getMarketNews,
  getMarketNewsIntelligence,
  getMarketNewsPredictions,
  getMarketOverview,
  getMarketPredictionDetail,
  getMarketPredictionHistory,
  getMarketQuotes,
  getMarketSectors,
} from "@/lib/api";
import { StateSurface } from "@/components/workbench-layout";
import { parseSymbolsInput } from "@/lib/backtests";
import { StockDetailPanel } from "@/components/stock-detail-panel";
import { KlineChart } from "@/components/kline-chart";
import {
  displayEvaluationStatus,
  displayNumber,
  displayPercent,
  displayPredictionDirection,
  displayReasoningEffort,
  displaySectorType,
  displaySignedPercent,
  displayText,
  displayThinkingType,
  displayWorkflowStatus,
} from "@/lib/display";
import type {
  MarketNewsIntelligenceResponse,
  MarketNewsPredictionsResponse,
  MarketNewsResponse,
  MarketOverview,
  MarketPrediction,
  MarketPredictionDetailResponse,
  MarketPredictionEvaluationResponse,
  MarketPredictionHistoryResponse,
  MarketPredictionMetadata,
  MarketQuotesResponse,
  MarketSectorsResponse,
} from "@/types/api";

const DEFAULT_SYMBOLS_INPUT = "000001,600036,601318";

type SectorType = "concept" | "industry";
type ThinkingType = "enabled" | "disabled";
type ReasoningEffort = "high" | "max";

type MarketWorkbenchData = {
  overview: MarketOverview | null;
  quotes: MarketQuotesResponse | null;
  sectors: MarketSectorsResponse | null;
  news: MarketNewsResponse | null;
  intelligence: MarketNewsIntelligenceResponse | null;
  predictions: MarketNewsPredictionsResponse | null;
  history: MarketPredictionHistoryResponse | null;
  detail: MarketPredictionDetailResponse | null;
  evaluation: MarketPredictionEvaluationResponse | null;
};

const INITIAL_DATA: MarketWorkbenchData = {
  overview: null,
  quotes: null,
  sectors: null,
  news: null,
  intelligence: null,
  predictions: null,
  history: null,
  detail: null,
  evaluation: null,
};

function MetricCard({ label, value, note }: { label: string; value: string | number; note?: string }) {
  return (
    <div className="grid gap-1 rounded-lg border border-border bg-muted/50 p-3">
      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">{label}</span>
      <span className="font-display text-lg font-bold">{value}</span>
      {note ? <span className="text-xs text-muted-foreground">{note}</span> : null}
    </div>
  );
}

function displayQualityScore(value?: number | null): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "暂无";
  }
  return displayPercent(value, 0);
}

function PredictionMetadataPanel({ metadata }: { metadata: MarketPredictionMetadata }) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <MetricCard
        label="预测提供方"
        value={displayWorkflowStatus(metadata.provider)}
        note={metadata.degraded ? "降级路径" : displayWorkflowStatus(metadata.requestMode || "remote")}
      />
      <MetricCard
        label="模型"
        value={displayWorkflowStatus(metadata.model)}
        note={`${displayThinkingType(metadata.thinkingType)} / ${displayReasoningEffort(metadata.reasoningEffort)}`}
      />
      <MetricCard
        label="结构版本"
        value={metadata.schemaVersion}
        note={`输入摘要 ${metadata.inputDigest}`}
      />
      <MetricCard
        label="上下文规模"
        value={`${metadata.newsItemCount} 条资讯`}
        note={`${metadata.keywordCount} 个关键词 / ${metadata.eventHintCount ?? 0} 个事件 / ${metadata.sectorHintCount} 个板块`}
      />
    </div>
  );
}

function PredictionDetailCard({
  prediction,
  evaluation,
  newsItems,
}: {
  prediction: MarketPrediction;
  evaluation?: MarketPredictionEvaluationResponse["evaluationItems"][number] | null;
  newsItems: MarketNewsResponse["items"];
}) {
  const evidenceItems = newsItems.filter((item) => prediction.sourceIds.includes(item.id));
  return (
    <Card className="mt-4">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">单条预测详情</span>
            <CardTitle className="font-display">{prediction.target}</CardTitle>
          </div>
          <Badge variant="secondary">
            {displayPredictionDirection(prediction.direction)} · {(prediction.confidence * 100).toFixed(0)}%
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <MetricCard label="目标类型" value={prediction.targetType} note={prediction.horizon} />
          <MetricCard label="模型评分" value={displayNumber(prediction.score)} note={prediction.predictionId || "暂无编号"} />
          <MetricCard
            label="评估状态"
            value={evaluation ? displayEvaluationStatus(evaluation.status) : "待评估"}
            note={evaluation?.note || ""}
          />
          <MetricCard
            label="实际涨跌幅"
            value={displaySignedPercent(evaluation?.actualChangePercent)}
          />
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {prediction.drivers.length ? (
            prediction.drivers.map((driver) => (
              <Badge variant="outline" key={`${prediction.target}-${driver}`}>{driver}</Badge>
            ))
          ) : (
            <Badge variant="outline">暂无驱动因子</Badge>
          )}
        </div>
        <div className="mt-4 grid gap-2">
          {evidenceItems.length ? (
            evidenceItems.slice(0, 4).map((item) => (
              <div className="rounded-lg border border-border p-3" key={item.id}>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{item.source}</span>
                  <span>{item.publishedAt}</span>
                </div>
                <strong className="mt-1 block text-sm">{item.title}</strong>
                <p className="mt-1 text-sm text-muted-foreground">{item.content}</p>
              </div>
            ))
          ) : (
            <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
              暂无可展示证据源。
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function EvaluationPanel({ evaluation }: { evaluation: MarketPredictionEvaluationResponse }) {
  const summary = evaluation.evaluationSummary;
  return (
    <div className="mt-4 grid gap-4">
      <div className="grid grid-cols-2 gap-3">
        <MetricCard
          label="命中率"
          value={typeof summary.hitRate === "number" ? `${(summary.hitRate * 100).toFixed(2)}%` : "待评估"}
          note={`${summary.hit} 命中 / ${summary.miss} 未命中`}
        />
        <MetricCard
          label="可评估"
          value={`${summary.assessable}/${summary.total}`}
          note={`${summary.pending} 条待评估，${summary.neutral} 条中性命中`}
        />
      </div>
      <div className="grid gap-2">
        {evaluation.evaluationItems.map((item) => (
          <div
            className="flex items-center justify-between rounded-lg border border-border p-3"
            key={item.predictionId}
          >
            <div>
              <strong className="text-sm">{item.target}</strong>
              <p className="text-xs text-muted-foreground">
                {displayPredictionDirection(item.direction)} · 实际涨跌 {displaySignedPercent(item.actualChangePercent)} · {item.note}
              </p>
            </div>
            <Badge variant={item.status === "miss" ? "destructive" : "secondary"}>
              {displayEvaluationStatus(item.status)}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MarketWorkbench() {
  const [symbolsInput, setSymbolsInput] = useState(DEFAULT_SYMBOLS_INPUT);
  const [sectorType, setSectorType] = useState<SectorType>("concept");
  const [thinkingType, setThinkingType] = useState<ThinkingType>("enabled");
  const [reasoningEffort, setReasoningEffort] = useState<ReasoningEffort>("high");
  const [data, setData] = useState<MarketWorkbenchData>(INITIAL_DATA);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedRunId, setSelectedRunId] = useState("");
  const [selectedPredictionId, setSelectedPredictionId] = useState("");
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [newsFilter, setNewsFilter] = useState<string>("all");

  async function loadData(
    nextSymbolsInput = symbolsInput,
    nextSectorType = sectorType,
    nextThinkingType = thinkingType,
    nextReasoningEffort = reasoningEffort,
  ) {
    const symbols = parseSymbolsInput(nextSymbolsInput);
    const quoteSymbols = symbols.length ? symbols : parseSymbolsInput(DEFAULT_SYMBOLS_INPUT);

    setLoading(true);
    setError("");
    setNotice("");

    const [
      overviewResult,
      quotesResult,
      sectorsResult,
      newsResult,
      intelligenceResult,
      predictionsResult,
    ] = await Promise.allSettled([
      getMarketOverview(),
      getMarketQuotes(quoteSymbols),
      getMarketSectors(nextSectorType, 8),
      getMarketNews(10),
      getMarketNewsIntelligence(60),
      getMarketNewsPredictions(60, symbols, {
        thinking: nextThinkingType,
        reasoningEffort: nextReasoningEffort,
      }),
    ]);

    const nextData: MarketWorkbenchData = { ...INITIAL_DATA };
    const errors: string[] = [];
    const notices: string[] = [];

    if (overviewResult.status === "fulfilled") {
      nextData.overview = overviewResult.value;
    } else {
      errors.push("市场总览加载失败");
    }

    if (quotesResult.status === "fulfilled") {
      nextData.quotes = quotesResult.value;
    } else {
      errors.push("监控报价加载失败");
    }

    if (sectorsResult.status === "fulfilled") {
      nextData.sectors = sectorsResult.value;
    } else {
      errors.push("板块列表加载失败");
    }

    if (newsResult.status === "fulfilled") {
      nextData.news = newsResult.value;
      if (newsResult.value.degraded) {
        notices.push("快讯已进入降级路径。");
      }
    } else {
      errors.push("最新快讯加载失败");
    }

    if (intelligenceResult.status === "fulfilled") {
      nextData.intelligence = intelligenceResult.value;
      if (intelligenceResult.value.degraded) {
        notices.push("情报结果来自降级新闻源。");
      }
    } else {
      errors.push("新闻情报加载失败");
    }

    let activeRunId = "";
    if (predictionsResult.status === "fulfilled") {
      nextData.predictions = predictionsResult.value;
      activeRunId = predictionsResult.value.runId || "";
      if (predictionsResult.value.predictionMetadata.degraded) {
        notices.push("预测结果来自本地启发式或降级模型路径。");
      }
    } else {
      errors.push("新闻预测加载失败");
    }

    await hydratePredictionLoop(nextData, activeRunId, errors, notices);

    const activePredictions = (nextData.detail || nextData.predictions)?.predictions || [];
    setSelectedRunId(activeRunId || nextData.history?.items[0]?.runId || "");
    setSelectedPredictionId(activePredictions[0]?.predictionId || "");
    setData(nextData);
    setError(
      errors.length >= 6
        ? "市场页所有请求都失败了，请确认后端服务是否启动，或稍后重试。"
        : errors.join(" / "),
    );
    setNotice(notices.join(" / "));
    setLoading(false);
  }

  async function hydratePredictionLoop(
    nextData: MarketWorkbenchData,
    runId: string,
    errors: string[],
    notices: string[],
  ) {
    const historyResult = await getMarketPredictionHistory(8)
      .then((value) => ({ status: "fulfilled" as const, value }))
      .catch((reason) => ({ status: "rejected" as const, reason }));
    if (historyResult.status === "fulfilled") {
      nextData.history = historyResult.value;
      if (historyResult.value.metadata.degraded) {
        notices.push("预测历史含有跳过记录，请查看历史元数据。");
      }
    } else {
      errors.push("预测历史加载失败");
    }

    if (!runId) {
      return;
    }

    const [detailResult, evaluationResult] = await Promise.allSettled([
      getMarketPredictionDetail(runId),
      evaluateMarketPredictionRun(runId),
    ]);
    if (detailResult.status === "fulfilled") {
      nextData.detail = detailResult.value;
    } else {
      notices.push("当前预测已生成，但详情接口暂不可用。");
    }
    if (evaluationResult.status === "fulfilled") {
      nextData.evaluation = evaluationResult.value;
      if (evaluationResult.value.metadata.degraded) {
        notices.push("预测评估使用降级行情结果。");
      }
    } else {
      notices.push("当前预测暂未完成行情评估。");
    }
  }

  async function loadPredictionRun(runId: string) {
    if (!runId || runId === selectedRunId) {
      return;
    }
    setLoading(true);
    setNotice("");
    setError("");
    const [detailResult, evaluationResult] = await Promise.allSettled([
      getMarketPredictionDetail(runId),
      evaluateMarketPredictionRun(runId),
    ]);

    const notices: string[] = [];
    setData((current) => {
      const next = { ...current };
      if (detailResult.status === "fulfilled") {
        next.detail = detailResult.value;
      } else {
        notices.push("历史预测详情加载失败。");
      }
      if (evaluationResult.status === "fulfilled") {
        next.evaluation = evaluationResult.value;
      } else {
        notices.push("历史预测评估加载失败。");
        next.evaluation = null;
      }
      return next;
    });
    setSelectedRunId(runId);
    setSelectedPredictionId(
      detailResult.status === "fulfilled"
        ? detailResult.value.predictions[0]?.predictionId || ""
        : "",
    );
    setNotice(notices.join(" / "));
    setLoading(false);
  }

  useEffect(() => {
    void loadData(DEFAULT_SYMBOLS_INPUT, "concept", "enabled", "high");
  }, []);

  const quotes = data.quotes?.items || [];
  const sectors = data.sectors?.items || [];
  const newsItems = data.news?.items || [];
  const keywords = data.intelligence?.keywords || [];
  const sectorHints = data.intelligence?.sectorHints || [];
  const activeRun = data.detail || data.predictions;
  const eventHints = activeRun?.eventHints || data.intelligence?.eventHints || [];
  const predictionRows = activeRun?.predictions || [];
  const historyRuns = data.history?.items || [];
  const channels = activeRun?.channels || data.news?.channels || [];
  const sourceQuality = activeRun?.sourceQuality || data.news?.sourceQuality;
  const dedupeMetadata = activeRun?.dedupeMetadata || data.news?.dedupeMetadata;
  const selectedPrediction =
    predictionRows.find((item) => item.predictionId === selectedPredictionId) ||
    predictionRows[0] ||
    null;
  const evaluationByPrediction = useMemo(
    () =>
      new Map(
        (data.evaluation?.evaluationItems || []).map((item) => [item.predictionId, item]),
      ),
    [data.evaluation],
  );
  const selectedEvaluation = selectedPrediction?.predictionId
    ? evaluationByPrediction.get(selectedPrediction.predictionId)
    : null;

  return (
    <div className="grid gap-6">
      {/* Header + Controls */}
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">预测控制台</span>
          <CardTitle className="font-display">行情监控</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? <StateSurface state="loading" title="正在刷新市场研究数据。" /> : null}
          {error ? <StateSurface state="error" title="部分市场请求失败。" detail={error} /> : null}
          {notice ? <StateSurface state="degraded" title="当前存在降级或待补充状态。" detail={notice} /> : null}

          <div className="mt-4 grid gap-4">
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <div className="grid gap-2">
                <Label>观察标的</Label>
                <Input value={symbolsInput} onChange={(e) => setSymbolsInput(e.target.value)} placeholder="000001,600036,601318" />
              </div>
              <div className="grid gap-2">
                <Label>板块类型</Label>
                <Select value={sectorType} onValueChange={(v) => setSectorType(v as SectorType)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="concept">概念板块</SelectItem>
                    <SelectItem value="industry">行业板块</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label>模型模式</Label>
                <Select value={thinkingType} onValueChange={(v) => setThinkingType(v as ThinkingType)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="enabled">思考模式</SelectItem>
                    <SelectItem value="disabled">非思考模式</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label>推理强度</Label>
                <Select value={reasoningEffort} onValueChange={(v) => setReasoningEffort(v as ReasoningEffort)} disabled={thinkingType === "disabled"}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="high">高</SelectItem>
                    <SelectItem value="max">最高</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Button disabled={loading} onClick={() => void loadData(symbolsInput, sectorType, thinkingType, reasoningEffort)}>
                <RefreshCw className="size-4" />
                {loading ? "刷新中" : "刷新研究数据"}
              </Button>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-5">
            <MetricCard
              label="主要行情源"
              value={displayText(data.overview?.primarySource, "未返回")}
              note={`备用源：${(data.overview?.fallbackSources || []).join(" -> ") || "无"}`}
            />
            <MetricCard
              label="监控报价"
              value={displayText(data.quotes?.source, "未返回")}
              note={`${quotes.length} 个监控标的`}
            />
            <MetricCard
              label="热门板块"
              value={displayText(data.sectors?.source, "未返回")}
              note={`${sectors.length} 个${displaySectorType(sectorType)}`}
            />
            <MetricCard
              label="模型模式"
              value={displayThinkingType(activeRun?.predictionMetadata.thinkingType)}
              note={`推理强度：${displayReasoningEffort(activeRun?.predictionMetadata.reasoningEffort)}`}
            />
            <MetricCard
              label="预测运行"
              value={displayText(activeRun?.runId, "尚未生成")}
              note={activeRun?.createdAt || "等待预测响应"}
            />
          </div>
        </CardContent>
      </Card>

      {/* Quotes + Sectors */}
      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">实时观察</span>
            <CardTitle className="font-display">监控标的报价</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {quotes.length ? (
                quotes.map((item) => (
                  <button
                    className={"w-full flex items-center justify-between rounded-lg border p-3 text-left transition-colors " +
                      (selectedSymbol === item.symbol
                        ? "border-primary bg-primary/5"
                        : "border-border hover:bg-muted/50")}
                    key={item.symbol}
                    type="button"
                    onClick={() => setSelectedSymbol(item.symbol === selectedSymbol ? "" : item.symbol)}
                  >
                    <div>
                      <strong className="text-sm">{item.name || "未知股票"}</strong>
                      <span className="ml-2 font-mono text-xs text-muted-foreground">{item.symbol}</span>
                      <p className="mt-1 text-xs text-muted-foreground">
                        开盘 {displayNumber(item.open)} · 最高 {displayNumber(item.high)} · 最低 {displayNumber(item.low)}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="font-display text-lg font-bold">{displayNumber(item.price)}</div>
                      <span className={(item.changePercent || 0) >= 0 ? "text-sm font-bold text-positive" : "text-sm font-bold text-warning"}>
                        {displaySignedPercent(item.changePercent)}
                      </span>
                    </div>
                  </button>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  暂无报价数据。
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">板块热度</span>
            <CardTitle className="font-display">热门板块</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {sectors.length ? (
                sectors.map((item) => (
                  <div className="flex items-center justify-between rounded-lg border border-border p-3" key={`${item.type}-${item.name}`}>
                    <div>
                      <strong className="text-sm">{item.name}</strong>
                      <p className="mt-1 text-xs text-muted-foreground">
                        领涨股 {item.leadingStock || "未知"} · 领涨幅 {displaySignedPercent(item.leadingStockChangePercent)} · 来源 {item.source}
                      </p>
                    </div>
                    <span className={(item.changePercent || 0) >= 0 ? "text-sm font-bold text-positive" : "text-sm font-bold text-warning"}>
                      {displaySignedPercent(item.changePercent)}
                    </span>
                  </div>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  暂无板块数据。
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Stock Detail + K-line */}
      {selectedSymbol ? (
        <section className="grid gap-6 lg:grid-cols-[1fr_2fr]">
          <StockDetailPanel symbol={selectedSymbol} />
          <KlineChart symbol={selectedSymbol} />
        </section>
      ) : null}

      {/* News + Intelligence */}
      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">多源资讯</span>
            <CardTitle className="font-display">市场快讯与来源质量</CardTitle>
          </CardHeader>
          <CardContent>
            {channels.length ? (
              <div className="mb-4 flex flex-wrap gap-2">
                {channels.map((channel) => (
                  <Badge variant="outline" key={`${channel.source}-${channel.status}`}>
                    {channel.name}：{displayWorkflowStatus(channel.status)} · {channel.itemCount}
                  </Badge>
                ))}
              </div>
            ) : null}
            {sourceQuality || dedupeMetadata ? (
              <div className="mb-4 grid grid-cols-3 gap-3">
                <MetricCard
                  label="质量评分"
                  value={displayQualityScore(sourceQuality?.qualityScore)}
                  note={`覆盖 ${displayQualityScore(sourceQuality?.coverageScore)} / 新鲜度 ${displayQualityScore(sourceQuality?.freshnessScore)}`}
                />
                <MetricCard
                  label="渠道覆盖"
                  value={`${sourceQuality?.succeededChannels ?? 0}/${sourceQuality?.queriedChannels ?? 0}`}
                  note={`失败 ${sourceQuality?.failedChannels ?? 0} / 降级 ${sourceQuality?.degradedChannels ?? 0}`}
                />
                <MetricCard
                  label="去重结果"
                  value={`${sourceQuality?.uniqueItems ?? newsItems.length}`}
                  note={`原始 ${sourceQuality?.totalItems ?? newsItems.length} / 重复 ${dedupeMetadata?.duplicateCount ?? sourceQuality?.duplicateItems ?? 0}`}
                />
              </div>
            ) : null}
            {sourceQuality?.qualityNotes?.length ? (
              <Alert className="mb-4">
                <AlertDescription>{sourceQuality.qualityNotes.join(" / ")}</AlertDescription>
              </Alert>
            ) : null}
            {newsItems.length ? (
              <div className="mb-3 flex flex-wrap gap-1">
                <Badge
                  variant={newsFilter === "all" ? "default" : "outline"}
                  className="cursor-pointer text-[0.6rem]"
                  onClick={() => setNewsFilter("all")}
                >
                  全部
                </Badge>
                <Badge
                  variant={newsFilter === "important" ? "default" : "outline"}
                  className="cursor-pointer text-[0.6rem]"
                  onClick={() => setNewsFilter("important")}
                >
                  重要
                </Badge>
                {Array.from(new Set(newsItems.flatMap(n => n.tags))).slice(0, 8).map(tag => (
                  <Badge
                    key={tag}
                    variant={newsFilter === tag ? "default" : "outline"}
                    className="cursor-pointer text-[0.6rem]"
                    onClick={() => setNewsFilter(newsFilter === tag ? "all" : tag)}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            ) : null}
            <div className="grid gap-2">
              {newsItems.length ? (
                newsItems
                  .filter(item => {
                    if (newsFilter === "all") return true
                    if (newsFilter === "important") return item.important
                    return item.tags.includes(newsFilter)
                  })
                  .slice(0, 8)
                  .map((item) => (
                  <div className="rounded-lg border border-border p-3" key={item.id}>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{item.publishedAt}</span>
                      <Badge variant={item.important ? "destructive" : "secondary"} className="text-[0.6rem]">
                        {item.important ? "重要" : "普通"}
                      </Badge>
                    </div>
                    <strong className="mt-1 block text-sm">{item.title}</strong>
                    <p className="mt-1 text-sm text-muted-foreground">{item.content}</p>
                    {item.tags.length ? (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {item.tags.slice(0, 5).map((tag) => (
                          <Badge variant="outline" className="text-[0.6rem]" key={`${item.id}-${tag}`}>{tag}</Badge>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  暂无新闻数据。
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">规则情报</span>
            <CardTitle className="font-display">情报分析</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {eventHints.length ? (
                eventHints.slice(0, 5).map((item) => (
                  <div className="rounded-lg border border-border p-3" key={item.eventType}>
                    <div className="flex items-center justify-between">
                      <strong className="text-sm">{item.label}</strong>
                      <Badge variant="secondary">
                        {displayPredictionDirection(item.signal)} · 评分 {displayNumber(item.score)}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      命中 {item.count} 次 · {item.relatedSymbols.length ? `相关标的 ${item.relatedSymbols.join(" / ")}` : "暂无明确股票代码"}
                    </p>
                    {item.matchedTitles.length ? (
                      <p className="mt-1 text-xs text-muted-foreground">{item.matchedTitles.slice(0, 2).join(" / ")}</p>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  当前规则未命中结构化事件提示。
                </div>
              )}
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {keywords.length ? (
                keywords.slice(0, 12).map((item) => (
                  <Badge variant="outline" key={item.keyword}>{item.keyword} · {item.count}</Badge>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  暂无关键词。
                </div>
              )}
            </div>

            <div className="mt-4 grid gap-2">
              {sectorHints.length ? (
                sectorHints.slice(0, 6).map((item) => (
                  <div className="rounded-lg border border-border p-3" key={`${item.boardType}-${item.name}`}>
                    <div className="flex items-center justify-between">
                      <strong className="text-sm">{item.name}</strong>
                      <Badge variant="secondary">评分 {item.score}</Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {item.boardType} · 关键词 {item.matchedKeywords.join(" / ")}
                    </p>
                  </div>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  当前规则未命中板块提示。
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Prediction + History */}
      <section className="grid gap-6 lg:grid-cols-[1.15fr_minmax(340px,0.85fr)]">
        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">预测详情</span>
            <CardTitle className="font-display">AI 预测</CardTitle>
          </CardHeader>
          <CardContent>
            {activeRun ? (
              <>
                <PredictionMetadataPanel metadata={activeRun.predictionMetadata} />

                <div className="mt-4 grid gap-2">
                  {predictionRows.length ? (
                    predictionRows.slice(0, 8).map((item) => {
                      const evaluation = item.predictionId
                        ? evaluationByPrediction.get(item.predictionId)
                        : null;
                      return (
                        <button
                          className={"w-full rounded-lg border p-3 text-left transition-colors " +
                            (selectedPrediction?.predictionId === item.predictionId
                              ? "border-primary bg-primary/5"
                              : "border-border hover:bg-muted/50")}
                          key={`${item.predictionId || item.targetType}-${item.target}`}
                          type="button"
                          onClick={() => setSelectedPredictionId(item.predictionId || "")}
                        >
                          <div className="flex items-center justify-between">
                            <strong className="text-sm">{item.target}</strong>
                            <Badge variant="secondary">
                              {displayPredictionDirection(item.direction)} · {(item.confidence * 100).toFixed(0)}%
                            </Badge>
                          </div>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {item.horizon} · 模型评分 {displayNumber(item.score)} · {evaluation ? displayEvaluationStatus(evaluation.status) : "等待评估"}
                          </p>
                        </button>
                      );
                    })
                  ) : (
                    <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                      暂无预测结果。
                    </div>
                  )}
                </div>

                {selectedPrediction ? (
                  <PredictionDetailCard
                    evaluation={selectedEvaluation}
                    newsItems={activeRun.items || []}
                    prediction={selectedPrediction}
                  />
                ) : null}

                <Alert className="mt-4" variant="destructive">
                  <AlertDescription>
                    {(activeRun.riskNotes || []).join(" / ") || "预测仅用于研究辅助，不构成投资建议。"}
                  </AlertDescription>
                </Alert>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  <MetricCard
                    label="回测预设"
                    value={activeRun.backtestHandoff.suggestedPreset}
                    note={activeRun.backtestHandoff.endpoint}
                  />
                  <MetricCard
                    label="交接标的"
                    value={`${activeRun.backtestHandoff.symbols.length}`}
                    note={activeRun.backtestHandoff.symbols.join(" / ") || "暂无明确股票代码"}
                  />
                </div>
              </>
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                暂无预测结果。
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">复盘历史</span>
            <CardTitle className="font-display">预测历史</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {historyRuns.length ? (
                historyRuns.map((run) => (
                  <button
                    className={"w-full rounded-lg border p-3 text-left transition-colors " +
                      (selectedRunId === run.runId
                        ? "border-primary bg-primary/5"
                        : "border-border hover:bg-muted/50")}
                    key={run.runId}
                    type="button"
                    onClick={() => void loadPredictionRun(run.runId)}
                  >
                    <div className="flex items-center justify-between">
                      <strong className="text-sm">{run.createdAt}</strong>
                      <Badge variant={run.degraded ? "destructive" : "secondary"}>
                        {run.degraded ? "降级" : "正常"} · {run.predictionCount}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {displayWorkflowStatus(run.model || "未知模型")} · {displayThinkingType(run.thinkingType)} · 质量 {displayQualityScore(run.qualityScore)}
                    </p>
                    {run.summary ? <p className="mt-1 text-xs text-muted-foreground">{run.summary}</p> : null}
                  </button>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                  暂无预测历史。
                </div>
              )}
            </div>

            {data.evaluation ? (
              <EvaluationPanel evaluation={data.evaluation} />
            ) : (
              <div className="mt-4 rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                尚未获得评估结果。生成预测或选择历史记录后会尝试评估。
              </div>
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
