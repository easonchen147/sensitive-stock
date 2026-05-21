"use client";

import { useEffect, useState } from "react";

import {
  getMarketNews,
  getMarketNewsIntelligence,
  getMarketOverview,
  getMarketQuotes,
  getMarketSectors,
} from "@/lib/api";
import { StateSurface } from "@/components/workbench-layout";
import { parseSymbolsInput } from "@/lib/backtests";
import type {
  MarketNewsIntelligenceResponse,
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
};

const INITIAL_DATA: MarketWorkbenchData = {
  overview: null,
  quotes: null,
  sectors: null,
  news: null,
  intelligence: null,
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

    const [overviewResult, quotesResult, sectorsResult, newsResult, intelligenceResult] =
      await Promise.allSettled([
        getMarketOverview(),
        getMarketQuotes(normalizedSymbols),
        getMarketSectors(nextSectorType, 8),
        getMarketNews(10),
        getMarketNewsIntelligence(60),
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

    setData(nextData);
    setError(
      errors.length === 5
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
          <h2 className="panel-title">Jin10 快讯</h2>
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
