"use client";

import { useEffect, useMemo, useState } from "react";

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

  async function loadData(
    nextSymbolsInput = symbolsInput,
    nextSectorType = sectorType,
    nextThinkingType = thinkingType,
    nextReasoningEffort = reasoningEffort,
  ) {
    const symbols = parseSymbolsInput(nextSymbolsInput);
    const normalizedSymbols = symbols.length ? symbols : parseSymbolsInput(DEFAULT_SYMBOLS_INPUT);

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
      getMarketQuotes(normalizedSymbols),
      getMarketSectors(nextSectorType, 8),
      getMarketNews(10),
      getMarketNewsIntelligence(60),
      getMarketNewsPredictions(60, normalizedSymbols, {
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
    <section className="stack">
      <article className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">预测控制台</div>
            <h2 className="panel-title">行情监控与多源资讯预测</h2>
            <p className="panel-subtitle">
              页面并行读取行情、板块、资讯、情报和预测接口，并把来源质量、模型模式、降级状态和评估结果完整展示出来。
            </p>
          </div>
        </div>

        {loading ? <StateSurface state="loading" title="正在刷新市场研究数据。" /> : null}
        {error ? <StateSurface state="error" title="部分市场请求失败。" detail={error} /> : null}
        {notice ? <StateSurface state="degraded" title="当前存在降级或待补充状态。" detail={notice} /> : null}

        <div className="toolbar-row">
          <div className="field-grid">
            <label htmlFor="watchlist">观察标的</label>
            <input
              id="watchlist"
              value={symbolsInput}
              onChange={(event) => setSymbolsInput(event.target.value)}
              placeholder="000001,600036,601318"
            />
          </div>
          <div className="field-grid">
            <label htmlFor="sectorType">板块类型</label>
            <select
              id="sectorType"
              value={sectorType}
              onChange={(event) => setSectorType(event.target.value as SectorType)}
            >
              <option value="concept">概念板块</option>
              <option value="industry">行业板块</option>
            </select>
          </div>
          <div className="field-grid">
            <label htmlFor="thinkingType">模型模式</label>
            <select
              id="thinkingType"
              value={thinkingType}
              onChange={(event) => setThinkingType(event.target.value as ThinkingType)}
            >
              <option value="enabled">思考模式</option>
              <option value="disabled">非思考模式</option>
            </select>
          </div>
          <div className="field-grid">
            <label htmlFor="reasoningEffort">推理强度</label>
            <select
              id="reasoningEffort"
              value={reasoningEffort}
              onChange={(event) => setReasoningEffort(event.target.value as ReasoningEffort)}
              disabled={thinkingType === "disabled"}
            >
              <option value="high">高</option>
              <option value="max">最高</option>
            </select>
          </div>
          <div className="toolbar-actions">
            <button
              className="secondary-button"
              disabled={loading}
              type="button"
              onClick={() => void loadData(symbolsInput, sectorType, thinkingType, reasoningEffort)}
            >
              {loading ? "刷新中" : "刷新研究数据"}
            </button>
          </div>
        </div>

        <div className="metric-grid">
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
      </article>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">实时观察</div>
          <h2 className="panel-title">监控标的报价</h2>
          <div className="quote-grid">
            {quotes.length ? (
              quotes.map((item) => (
                <div className="quote-card" key={item.symbol}>
                  <div className="status-head">
                    <strong>
                      {item.name || "未知股票"} <span className="mono-inline">{item.symbol}</span>
                    </strong>
                    <span
                      className="quote-change"
                      data-tone={(item.changePercent || 0) >= 0 ? "positive" : "warning"}
                    >
                      {displaySignedPercent(item.changePercent)}
                    </span>
                  </div>
                  <div className="quote-price">{displayNumber(item.price)}</div>
                  <p>
                    开盘 {displayNumber(item.open)} · 最高 {displayNumber(item.high)} · 最低{" "}
                    {displayNumber(item.low)}
                  </p>
                </div>
              ))
            ) : (
              <StateSurface state="empty" title="暂无报价数据。" />
            )}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">板块热度</div>
          <h2 className="panel-title">热门板块</h2>
          <div className="status-list">
            {sectors.length ? (
              sectors.map((item) => (
                <div className="status-item" data-status="migrated" key={`${item.type}-${item.name}`}>
                  <div className="status-head">
                    <strong>{item.name}</strong>
                    <span
                      className="quote-change"
                      data-tone={(item.changePercent || 0) >= 0 ? "positive" : "warning"}
                    >
                      {displaySignedPercent(item.changePercent)}
                    </span>
                  </div>
                  <p>
                    领涨股 {item.leadingStock || "未知"} · 领涨幅{" "}
                    {displaySignedPercent(item.leadingStockChangePercent)} · 来源 {item.source}
                  </p>
                </div>
              ))
            ) : (
              <StateSurface state="empty" title="暂无板块数据。" />
            )}
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">多源资讯</div>
          <h2 className="panel-title">市场快讯与来源质量</h2>
          {channels.length ? (
            <div className="tag-row">
              {channels.map((channel) => (
                <span className="tag-chip" key={`${channel.source}-${channel.status}`}>
                  {channel.name}：{displayWorkflowStatus(channel.status)} · {channel.itemCount}
                </span>
              ))}
            </div>
          ) : null}
          {sourceQuality || dedupeMetadata ? (
            <div className="metric-grid">
              <MetricCard
                label="质量评分"
                value={displayQualityScore(sourceQuality?.qualityScore)}
                note={`覆盖 ${displayQualityScore(sourceQuality?.coverageScore)} / 新鲜度 ${displayQualityScore(
                  sourceQuality?.freshnessScore,
                )}`}
              />
              <MetricCard
                label="渠道覆盖"
                value={`${sourceQuality?.succeededChannels ?? 0}/${sourceQuality?.queriedChannels ?? 0}`}
                note={`失败 ${sourceQuality?.failedChannels ?? 0} / 降级 ${
                  sourceQuality?.degradedChannels ?? 0
                }`}
              />
              <MetricCard
                label="去重结果"
                value={`${sourceQuality?.uniqueItems ?? newsItems.length}`}
                note={`原始 ${sourceQuality?.totalItems ?? newsItems.length} / 重复 ${
                  dedupeMetadata?.duplicateCount ?? sourceQuality?.duplicateItems ?? 0
                }`}
              />
            </div>
          ) : null}
          {sourceQuality?.qualityNotes?.length ? (
            <div className="banner banner-neutral">{sourceQuality.qualityNotes.join(" / ")}</div>
          ) : null}
          <div className="news-list">
            {newsItems.length ? (
              newsItems.slice(0, 8).map((item) => (
                <article className="news-item" key={item.id}>
                  <div className="news-meta">
                    <span>{item.publishedAt}</span>
                    <span>{item.important ? "重要" : "普通"}</span>
                  </div>
                  <h3 className="news-title">{item.title}</h3>
                  <p className="news-copy">{item.content}</p>
                  {item.tags.length ? (
                    <div className="tag-row">
                      {item.tags.slice(0, 5).map((tag) => (
                        <span className="tag-chip" key={`${item.id}-${tag}`}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))
            ) : (
              <StateSurface state="empty" title="暂无新闻数据。" />
            )}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">规则情报</div>
          <h2 className="panel-title">关键词与板块提示</h2>
          <p className="panel-subtitle">
            这里展示后端已提供的关键词提取和板块命中提示，只呈现可追溯的规则结果。
          </p>

          <div className="keyword-cloud">
            {keywords.length ? (
              keywords.slice(0, 12).map((item) => (
                <span className="keyword-pill" key={item.keyword}>
                  {item.keyword} · {item.count}
                </span>
              ))
            ) : (
              <StateSurface state="empty" title="暂无关键词。" />
            )}
          </div>

          <div className="status-list">
            {sectorHints.length ? (
              sectorHints.slice(0, 6).map((item) => (
                <div className="status-item" data-status="migrated" key={`${item.boardType}-${item.name}`}>
                  <div className="status-head">
                    <strong>{item.name}</strong>
                    <span className="status-pill">评分 {item.score}</span>
                  </div>
                  <p>
                    {item.boardType} · 关键词 {item.matchedKeywords.join(" / ")}
                  </p>
                </div>
              ))
            ) : (
              <StateSurface state="empty" title="当前规则未命中板块提示。" />
            )}
          </div>
        </article>
      </section>

      <section className="workbench-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">预测详情</div>
              <h2 className="panel-title">多源资讯预测与回测交接</h2>
              <p className="panel-subtitle">
                后端优先使用 DeepSeek V4 Flash；未配置密钥或模型失败时会明确降级到本地启发式预测，并保留回测交接参数。
              </p>
            </div>
          </div>

          {activeRun ? (
            <>
              <PredictionMetadataPanel metadata={activeRun.predictionMetadata} />

              <div className="status-list">
                {predictionRows.length ? (
                  predictionRows.slice(0, 8).map((item) => {
                    const evaluation = item.predictionId
                      ? evaluationByPrediction.get(item.predictionId)
                      : null;
                    return (
                      <button
                        className="prediction-row"
                        data-active={selectedPrediction?.predictionId === item.predictionId}
                        key={`${item.predictionId || item.targetType}-${item.target}`}
                        type="button"
                        onClick={() => setSelectedPredictionId(item.predictionId || "")}
                      >
                        <div className="status-head">
                          <strong>{item.target}</strong>
                          <span className="status-pill">
                            {displayPredictionDirection(item.direction)} ·{" "}
                            {(item.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p>
                          {item.horizon} · 模型评分 {displayNumber(item.score)} ·{" "}
                          {evaluation ? displayEvaluationStatus(evaluation.status) : "等待评估"}
                        </p>
                      </button>
                    );
                  })
                ) : (
                  <StateSurface state="empty" title="暂无预测结果。" />
                )}
              </div>

              {selectedPrediction ? (
                <PredictionDetailCard
                  evaluation={selectedEvaluation}
                  newsItems={activeRun.items || []}
                  prediction={selectedPrediction}
                />
              ) : null}

              <div className="banner banner-warning">
                {(activeRun.riskNotes || []).join(" / ") || "预测仅用于研究辅助，不构成投资建议。"}
              </div>

              <div className="metric-grid">
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
            <StateSurface state="empty" title="暂无预测结果。" />
          )}
        </article>

        <aside className="panel">
          <div className="eyebrow">复盘历史</div>
          <h2 className="panel-title">预测历史与评估</h2>
          <p className="panel-subtitle">
            最近运行会写入本地 JSONL 历史。选择历史记录后，页面会重新读取详情和最新行情评估。
          </p>

          <div className="status-list">
            {historyRuns.length ? (
              historyRuns.map((run) => (
                <button
                  className="history-row"
                  data-active={selectedRunId === run.runId}
                  key={run.runId}
                  type="button"
                  onClick={() => void loadPredictionRun(run.runId)}
                >
                  <div className="status-head">
                    <strong>{run.createdAt}</strong>
                    <span className="status-pill">
                      {run.degraded ? "降级" : "正常"} · {run.predictionCount}
                    </span>
                  </div>
                  <p>
                    {displayText(run.model, "未知模型")} · {displayThinkingType(run.thinkingType)} ·
                    质量 {displayQualityScore(run.qualityScore)}
                  </p>
                  {run.summary ? <p>{run.summary}</p> : null}
                </button>
              ))
            ) : (
              <StateSurface state="empty" title="暂无预测历史。" />
            )}
          </div>

          {data.evaluation ? (
            <EvaluationPanel evaluation={data.evaluation} />
          ) : (
            <StateSurface state="empty" title="尚未获得评估结果。" detail="生成预测或选择历史记录后会尝试评估。" />
          )}
        </aside>
      </section>
    </section>
  );
}

function PredictionMetadataPanel({ metadata }: { metadata: MarketPredictionMetadata }) {
  return (
    <div className="metric-grid">
      <MetricCard
        label="预测提供方"
        value={displayText(metadata.provider)}
        note={metadata.degraded ? "降级路径" : displayWorkflowStatus(metadata.requestMode || "remote")}
      />
      <MetricCard
        label="模型"
        value={metadata.model}
        note={`${displayThinkingType(metadata.thinkingType)} / ${displayReasoningEffort(
          metadata.reasoningEffort,
        )}`}
      />
      <MetricCard
        label="结构版本"
        value={metadata.schemaVersion}
        note={`输入摘要 ${metadata.inputDigest}`}
      />
      <MetricCard
        label="上下文规模"
        value={`${metadata.newsItemCount} 条资讯`}
        note={`${metadata.keywordCount} 个关键词 / ${metadata.sectorHintCount} 个板块提示`}
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
    <article className="detail-card">
      <div className="status-head">
        <div>
          <div className="eyebrow">单条预测详情</div>
          <h3 className="detail-title">{prediction.target}</h3>
        </div>
        <span className="status-pill">
          {displayPredictionDirection(prediction.direction)} · {(prediction.confidence * 100).toFixed(0)}%
        </span>
      </div>
      <div className="metric-grid">
        <MetricCard label="目标类型" value={prediction.targetType} note={prediction.horizon} />
        <MetricCard label="模型评分" value={displayNumber(prediction.score)} note={prediction.predictionId || "暂无编号"} />
        <MetricCard
          label="评估状态"
          value={evaluation ? displayEvaluationStatus(evaluation.status) : "待评估"}
          note={evaluation?.note || "等待行情映射和评估结果。"}
        />
        <MetricCard
          label="实际涨跌幅"
          value={displaySignedPercent(evaluation?.actualChangePercent)}
          note="仅在能映射到股票代码时展示。"
        />
      </div>
      <div className="tag-row">
        {prediction.drivers.length ? (
          prediction.drivers.map((driver) => (
            <span className="tag-chip" key={`${prediction.target}-${driver}`}>
              {driver}
            </span>
          ))
        ) : (
          <span className="tag-chip">暂无驱动因子</span>
        )}
      </div>
      <div className="status-list">
        {evidenceItems.length ? (
          evidenceItems.slice(0, 4).map((item) => (
            <div className="status-item" data-status="migrated" key={item.id}>
              <div className="news-meta">
                <span>{item.source}</span>
                <span>{item.publishedAt}</span>
              </div>
              <strong>{item.title}</strong>
              <p>{item.content}</p>
            </div>
          ))
        ) : (
          <StateSurface state="empty" title="暂无可展示证据源。" />
        )}
      </div>
    </article>
  );
}

function EvaluationPanel({ evaluation }: { evaluation: MarketPredictionEvaluationResponse }) {
  const summary = evaluation.evaluationSummary;
  return (
    <div className="evaluation-panel">
      <div className="metric-grid">
        <MetricCard
          label="命中率"
          value={
            typeof summary.hitRate === "number"
              ? `${(summary.hitRate * 100).toFixed(2)}%`
              : "待评估"
          }
          note={`${summary.hit} 命中 / ${summary.miss} 未命中`}
        />
        <MetricCard
          label="可评估"
          value={`${summary.assessable}/${summary.total}`}
          note={`${summary.pending} 条待评估，${summary.neutral} 条中性命中`}
        />
      </div>
      <div className="status-list">
        {evaluation.evaluationItems.map((item) => (
          <div className="status-item" data-status={item.status === "miss" ? "skeleton" : "migrated"} key={item.predictionId}>
            <div className="status-head">
              <strong>{item.target}</strong>
              <span className="status-pill">{displayEvaluationStatus(item.status)}</span>
            </div>
            <p>
              {displayPredictionDirection(item.direction)} · 实际涨跌{" "}
              {displaySignedPercent(item.actualChangePercent)} · {item.note}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  note,
}: {
  label: string;
  value: string | number;
  note?: string;
}) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <div className="metric-value">{value}</div>
      {note ? <div className="metric-note">{note}</div> : null}
    </div>
  );
}

function displayQualityScore(value?: number | null): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "暂无";
  }
  return displayPercent(value, 0);
}
