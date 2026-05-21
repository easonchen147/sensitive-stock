"use client";

import { useEffect, useState } from "react";

import {
  getMarketNews,
  getMarketNewsIntelligence,
  getMarketNewsPredictions,
  getMarketOverview,
  getMarketQuotes,
  getMarketSectors,
} from "@/lib/api";
import { StateSurface } from "@/components/workbench-layout";
import { parseSymbolsInput } from "@/lib/backtests";
import type {
  MarketNewsIntelligenceResponse,
  MarketNewsPredictionsResponse,
  MarketNewsResponse,
  MarketOverview,
  MarketQuotesResponse,
  MarketSectorsResponse,
} from "@/types/api";

const DEFAULT_SYMBOLS_INPUT = "000001,600036,601318";

type SectorType = "concept" | "industry";

type MarketWorkbenchData = {
  overview: MarketOverview | null;
  quotes: MarketQuotesResponse | null;
  sectors: MarketSectorsResponse | null;
  news: MarketNewsResponse | null;
  intelligence: MarketNewsIntelligenceResponse | null;
  predictions: MarketNewsPredictionsResponse | null;
};

const INITIAL_DATA: MarketWorkbenchData = {
  overview: null,
  quotes: null,
  sectors: null,
  news: null,
  intelligence: null,
  predictions: null,
};

export function MarketWorkbench() {
  const [symbolsInput, setSymbolsInput] = useState(DEFAULT_SYMBOLS_INPUT);
  const [sectorType, setSectorType] = useState<SectorType>("concept");
  const [data, setData] = useState<MarketWorkbenchData>(INITIAL_DATA);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadData(nextSymbolsInput = symbolsInput, nextSectorType = sectorType) {
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
    ] =
      await Promise.allSettled([
        getMarketOverview(),
        getMarketQuotes(normalizedSymbols),
        getMarketSectors(nextSectorType, 8),
        getMarketNews(10),
        getMarketNewsIntelligence(60),
        getMarketNewsPredictions(60, normalizedSymbols),
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
        notices.push("快讯已降级到 Jin10 公共 feed。");
      }
    } else {
      errors.push("最新快讯加载失败");
    }

    if (intelligenceResult.status === "fulfilled") {
      nextData.intelligence = intelligenceResult.value;
      if (intelligenceResult.value.degraded) {
        notices.push("intelligence 结果来自降级新闻源。");
      }
    } else {
      errors.push("新闻 intelligence 加载失败");
    }

    if (predictionsResult.status === "fulfilled") {
      nextData.predictions = predictionsResult.value;
      if (predictionsResult.value.predictionMetadata.degraded) {
        notices.push("预测结果来自本地启发式或降级模型路径。");
      }
    } else {
      errors.push("新闻预测加载失败");
    }

    setData(nextData);
    setError(
      errors.length === 6
        ? "市场页所有请求都失败了，请确认 backend 是否启动，或稍后重试。"
        : errors.join(" / "),
    );
    setNotice(notices.join(" / "));
    setLoading(false);
  }

  useEffect(() => {
    void loadData(DEFAULT_SYMBOLS_INPUT, "concept");
  }, []);

  const quotes = data.quotes?.items || [];
  const sectors = data.sectors?.items || [];
  const newsItems = data.news?.items || [];
  const keywords = data.intelligence?.keywords || [];
  const sectorHints = data.intelligence?.sectorHints || [];
  const predictionRows = data.predictions?.predictions || [];
  const channels = data.predictions?.channels || data.news?.channels || [];
  const sourceQuality = data.predictions?.sourceQuality || data.news?.sourceQuality;
  const dedupeMetadata = data.predictions?.dedupeMetadata || data.news?.dedupeMetadata;

  return (
    <section className="stack">
      <article className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">Market Controls</div>
            <h2 className="panel-title">行情监控与 intelligence 工作台</h2>
            <p className="panel-subtitle">
              页面会直接并行读取 backend market/news API，并把真实的 source、degraded 和错误状态展示出来。
            </p>
          </div>
        </div>

        {loading ? <StateSurface state="loading" title="Refreshing market data." /> : null}
        {error ? <StateSurface state="error" title="Some market requests failed." detail={error} /> : null}
        {notice ? <StateSurface state="degraded" title="Market data is degraded." detail={notice} /> : null}

        <div className="toolbar-row">
          <div className="field-grid">
            <label htmlFor="watchlist">Watchlist</label>
            <input
              id="watchlist"
              value={symbolsInput}
              onChange={(event) => setSymbolsInput(event.target.value)}
              placeholder="000001,600036,601318"
            />
          </div>
          <div className="field-grid">
            <label htmlFor="sectorType">Sector Type</label>
            <select
              id="sectorType"
              value={sectorType}
              onChange={(event) => setSectorType(event.target.value as SectorType)}
            >
              <option value="concept">concept</option>
              <option value="industry">industry</option>
            </select>
          </div>
          <div className="toolbar-actions">
            <button
              className="secondary-button"
              disabled={loading}
              type="button"
              onClick={() => void loadData(symbolsInput, sectorType)}
            >
              {loading ? "Refreshing" : "Refresh Data"}
            </button>
          </div>
        </div>

        <div className="metric-grid">
          <MetricCard
            label="Primary Source"
            value={data.overview?.primarySource || "N/A"}
            note={`fallback: ${(data.overview?.fallbackSources || []).join(" -> ") || "none"}`}
          />
          <MetricCard
            label="Quotes"
            value={data.quotes?.source || "N/A"}
            note={`${quotes.length} 个监控标的`}
          />
          <MetricCard
            label="Sectors"
            value={data.sectors?.source || "N/A"}
            note={`${sectors.length} 个${sectorType}板块`}
          />
          <MetricCard
            label="News"
            value={data.news?.source || "N/A"}
            note={data.news?.degraded ? "degraded" : "latest feed"}
          />
          <MetricCard
            label="Prediction"
            value={data.predictions?.predictionMetadata.provider || "N/A"}
            note={
              data.predictions
                ? `${data.predictions.predictionMetadata.model} / ${
                    data.predictions.predictionMetadata.cached ? "cached" : "fresh"
                  }`
                : "no model"
            }
          />
        </div>
      </article>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="eyebrow">Watchlist Quotes</div>
          <h2 className="panel-title">监控标的</h2>
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
                      {formatSignedPercent(item.changePercent)}
                    </span>
                  </div>
                  <div className="quote-price">{formatPrice(item.price)}</div>
                  <p>
                    开 {formatPrice(item.open)} · 高 {formatPrice(item.high)} · 低{" "}
                    {formatPrice(item.low)}
                  </p>
                </div>
              ))
            ) : (
              <StateSurface state="empty" title="暂无报价数据。" />
            )}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">Hot Sectors</div>
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
                      {formatSignedPercent(item.changePercent)}
                    </span>
                  </div>
                  <p>
                    领涨股 {item.leadingStock || "未知"} · 涨幅{" "}
                    {formatSignedPercent(item.leadingStockChangePercent)} · source {item.source}
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
          <div className="eyebrow">Latest News</div>
          <h2 className="panel-title">多源市场快讯</h2>
          {channels.length ? (
            <div className="tag-row">
              {channels.map((channel) => (
                <span className="tag-chip" key={`${channel.source}-${channel.status}`}>
                  {channel.name}: {channel.status} · {channel.itemCount}
                </span>
              ))}
            </div>
          ) : null}
          {sourceQuality || dedupeMetadata ? (
            <div className="metric-grid">
              <MetricCard
                label="Source Coverage"
                value={`${sourceQuality?.succeededChannels ?? 0}/${sourceQuality?.queriedChannels ?? 0}`}
                note={`failed ${sourceQuality?.failedChannels ?? 0} / degraded ${
                  sourceQuality?.degradedChannels ?? 0
                }`}
              />
              <MetricCard
                label="Unique News"
                value={`${sourceQuality?.uniqueItems ?? newsItems.length}`}
                note={`${sourceQuality?.totalItems ?? newsItems.length} raw items`}
              />
              <MetricCard
                label="Duplicates"
                value={`${dedupeMetadata?.duplicateCount ?? sourceQuality?.duplicateItems ?? 0}`}
                note={dedupeMetadata?.strategy || "source metadata unavailable"}
              />
            </div>
          ) : null}
          <div className="news-list">
            {newsItems.length ? (
              newsItems.slice(0, 8).map((item) => (
                <article className="news-item" key={item.id}>
                  <div className="news-meta">
                    <span>{item.publishedAt}</span>
                    <span>{item.important ? "important" : "normal"}</span>
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
          <div className="eyebrow">Rule-Based Intelligence</div>
          <h2 className="panel-title">关键词与板块提示</h2>
          <p className="panel-subtitle">
            这里展示的是当前 backend 已提供的关键词提取和板块命中提示骨架，不会伪装成完整 AI 分析结论。
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
                    <span className="status-pill">{item.score}</span>
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

      <article className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">DeepSeek Prediction Loop</div>
            <h2 className="panel-title">多源资讯预测与回测交接</h2>
            <p className="panel-subtitle">
              backend 会优先使用 DeepSeek V4 Flash；未配置 key 或模型失败时会明确降级到本地启发式预测，并给出 AKQuant 回测交接参数。
            </p>
          </div>
        </div>

        {data.predictions ? (
          <>
            <div className="metric-grid">
              <MetricCard
                label="Provider"
                value={data.predictions.predictionMetadata.provider}
                note={data.predictions.predictionMetadata.degraded ? "degraded" : "remote model"}
              />
              <MetricCard
                label="Model"
                value={data.predictions.predictionMetadata.model}
                note={data.predictions.predictionSummary || "structured prediction"}
              />
              <MetricCard
                label="Schema"
                value={data.predictions.predictionMetadata.schemaVersion}
                note={`input ${data.predictions.predictionMetadata.inputDigest}`}
              />
              <MetricCard
                label="Context"
                value={`${data.predictions.predictionMetadata.newsItemCount} news`}
                note={`${data.predictions.predictionMetadata.keywordCount} keywords / ${
                  data.predictions.predictionMetadata.sectorHintCount
                } sector hints`}
              />
              <MetricCard
                label="Backtest Preset"
                value={data.predictions.backtestHandoff.suggestedPreset}
                note={data.predictions.backtestHandoff.endpoint}
              />
            </div>

            {data.predictions.predictionMetadata.warnings?.length ? (
              <StateSurface
                state="degraded"
                title="Prediction path is degraded."
                detail={data.predictions.predictionMetadata.warnings.join(" / ")}
              />
            ) : null}

            <div className="status-list">
              {predictionRows.length ? (
                predictionRows.slice(0, 6).map((item) => (
                  <div className="status-item" data-status="migrated" key={`${item.targetType}-${item.target}`}>
                    <div className="status-head">
                      <strong>{item.target}</strong>
                      <span className="status-pill">
                        {item.direction} · {(item.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p>
                      {item.horizon} · score {item.score} · drivers {item.drivers.join(" / ")}
                    </p>
                    {item.sourceIds.length ? (
                      <div className="tag-row">
                        {item.sourceIds.slice(0, 4).map((sourceId) => (
                          <span className="tag-chip" key={`${item.target}-${sourceId}`}>
                            evidence {sourceId}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ))
              ) : (
                <StateSurface state="empty" title="暂无预测结果。" />
              )}
            </div>

            <div className="banner banner-warning">
              {data.predictions.riskNotes.join(" / ")}
            </div>
          </>
        ) : (
          <StateSurface state="empty" title="暂无预测结果。" />
        )}
      </article>
    </section>
  );
}

function MetricCard({
  label,
  value,
  note,
}: {
  label: string;
  value: string;
  note: string;
}) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <div className="metric-value">{value}</div>
      <div className="metric-note">{note}</div>
    </div>
  );
}

function formatSignedPercent(value?: number | null): string {
  if (typeof value !== "number") {
    return "N/A";
  }
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatPrice(value?: number | null): string {
  if (typeof value !== "number") {
    return "N/A";
  }
  return value.toFixed(2);
}
