"use client";

import { useState } from "react";

import {
  analyzeFactors,
  exportScreener,
  optimizePortfolio,
  runDiagnosis,
  runScreener,
} from "@/lib/api";
import { MetadataState, StateSurface } from "@/components/workbench-layout";
import {
  displayPortfolioObjective,
} from "@/lib/display";
import type {
  CapabilityMetadata,
  DiagnosisResponse,
  FactorAnalysisResponse,
  PortfolioOptimizationResponse,
  ScreenerExportResponse,
  ScreenerRunResponse,
} from "@/types/api";

const DEFAULT_START = "2025-01-01";
const DEFAULT_END = "2025-03-31";

function parseSymbols(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function MetadataBanner({ metadata }: { metadata?: CapabilityMetadata }) {
  return <MetadataState metadata={metadata} />;
}

export function ScreenerWorkbench() {
  const [symbols, setSymbols] = useState("000001,600000,300750,000858");
  const [prompt, setPrompt] = useState("低价区间内保持强势动量");
  const [minChange, setMinChange] = useState("0");
  const [maxPrice, setMaxPrice] = useState("80");
  const [result, setResult] = useState<ScreenerRunResponse | null>(null);
  const [exportResult, setExportResult] = useState<ScreenerExportResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const payload = {
    universe: parseSymbols(symbols),
    prompt,
    filters: {
      minChangePercent: Number(minChange),
      maxPrice: Number(maxPrice),
    },
    sortBy: "score" as const,
    limit: 10,
    backtestStartDate: DEFAULT_START,
    backtestEndDate: DEFAULT_END,
  };

  async function submit() {
    setLoading(true);
    setError("");
    try {
      setResult(await runScreener(payload));
      setExportResult(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "选股请求失败。");
    } finally {
      setLoading(false);
    }
  }

  async function exportRows() {
    setLoading(true);
    setError("");
    try {
      setExportResult(await exportScreener(payload));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "选股导出失败。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">条件选股</div>
        <h1 className="panel-title">结构化股票筛选</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>标的池</label>
            <input value={symbols} onChange={(event) => setSymbols(event.target.value)} />
          </div>
          <div className="field-grid">
            <label>自然语言条件</label>
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} />
          </div>
          <div className="field-row">
            <div className="field-grid">
              <label>最小涨跌幅</label>
              <input value={minChange} onChange={(event) => setMinChange(event.target.value)} />
            </div>
            <div className="field-grid">
              <label>最高价格</label>
              <input value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} />
            </div>
          </div>
          <div className="submit-row">
            <button className="primary-button" disabled={loading} onClick={submit}>
              运行选股
            </button>
            <button className="secondary-button" disabled={loading || !result} onClick={exportRows}>
              导出结果
            </button>
          </div>
          {loading ? (
            <StateSurface state="loading" title="选股请求运行中。" />
          ) : null}
          {error ? <StateSurface state="error" title="选股请求失败。" detail={error} /> : null}
        </div>
      </article>

      <article className="panel">
        <div className="eyebrow">筛选结果</div>
        <h2 className="panel-title">候选标的排序</h2>
        <MetadataBanner metadata={result?.metadata} />
        <div className="results-stack">
          {result?.items.length ? (
            result.items.map((item) => (
            <div className="result-card" key={item.symbol}>
              <div className="result-header">
                <div>
                  <h3>{item.symbol}</h3>
                  <p>{item.name}</p>
                </div>
                <span className="status-pill">评分 {item.score.toFixed(2)}</span>
              </div>
              <div className="metric-grid">
                <div className="summary-item">
                  <span className="metric-label">价格</span>
                  <strong>{item.price.toFixed(2)}</strong>
                </div>
                <div className="summary-item">
                  <span className="metric-label">涨跌幅</span>
                  <strong>{item.changePercent.toFixed(2)}%</strong>
                </div>
              </div>
            </div>
            ))
          ) : (
            <StateSurface
              state={result ? "empty" : "empty"}
              title={result ? "当前条件没有匹配候选。" : "运行一次选股后查看候选标的。"}
              detail={result ? "已应用条件仍会保留在响应摘要中。" : undefined}
            />
          )}
        </div>
        {exportResult ? (
          <div className="banner banner-neutral">
            导出已准备：{exportResult.rows.length} 行，{exportResult.columns.length} 列。
          </div>
        ) : null}
      </article>
    </section>
  );
}

export function DiagnosisWorkbench() {
  const [symbol, setSymbol] = useState("000001");
  const [result, setResult] = useState<DiagnosisResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      setResult(
        await runDiagnosis({
          symbol,
          startDate: DEFAULT_START,
          endDate: DEFAULT_END,
          includeNews: true,
        }),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "诊股请求失败。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">诊股报告</div>
        <h1 className="panel-title">结构化股票诊断</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>股票代码</label>
            <input value={symbol} onChange={(event) => setSymbol(event.target.value)} />
          </div>
          <button className="primary-button" disabled={loading} onClick={submit}>
            生成报告
          </button>
          {loading ? <StateSurface state="loading" title="诊股报告生成中。" /> : null}
          {error ? <StateSurface state="error" title="诊股请求失败。" detail={error} /> : null}
        </div>
      </article>
      <article className="panel">
        <div className="eyebrow">报告内容</div>
        <h2 className="panel-title">{result?.name || "等待输入标的"}</h2>
        <MetadataBanner metadata={result?.metadata} />
        <div className="insight-list">
          {result?.sections.length ? (
            result.sections.map((section) => (
            <div className="insight-card" data-tone={section.tone} key={section.title}>
              <strong>{section.title}</strong>
              <p>{section.summary}</p>
            </div>
            ))
          ) : (
            <StateSurface state="empty" title="生成报告后查看结构化段落。" />
          )}
        </div>
      </article>
    </section>
  );
}

export function FactorWorkbench() {
  const [symbol, setSymbol] = useState("000001");
  const [result, setResult] = useState<FactorAnalysisResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      setResult(
        await analyzeFactors({
          symbol,
          startDate: DEFAULT_START,
          endDate: DEFAULT_END,
          forwardDays: 5,
          topN: 6,
        }),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "因子分析失败。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">因子研究</div>
        <h1 className="panel-title">因子分析</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>股票代码</label>
            <input value={symbol} onChange={(event) => setSymbol(event.target.value)} />
          </div>
          <button className="primary-button" disabled={loading} onClick={submit}>
            分析因子
          </button>
          {loading ? <StateSurface state="loading" title="因子分析运行中。" /> : null}
          {error ? <StateSurface state="error" title="因子分析失败。" detail={error} /> : null}
        </div>
      </article>
      <article className="panel">
        <div className="eyebrow">IC 排名</div>
        <h2 className="panel-title">{result?.symbol || "尚未分析"}</h2>
        <MetadataBanner metadata={result?.metadata} />
        <div className="status-list">
          {result?.rankedFactors.length ? (
            result.rankedFactors.map((item) => (
            <div className="status-item" data-status="migrated" key={item.name}>
              <div className="status-head">
                <strong>{item.name}</strong>
                <span className="status-pill">{item.ic.toFixed(3)}</span>
              </div>
            </div>
            ))
          ) : (
            <StateSurface state="empty" title="运行因子分析后查看排名。" />
          )}
        </div>
      </article>
    </section>
  );
}

export function PortfolioWorkbench() {
  const [symbols, setSymbols] = useState("000001,600000,300750");
  const [objective, setObjective] =
    useState<"equal_weight" | "minimum_variance" | "maximum_sharpe" | "risk_parity">(
      "maximum_sharpe",
    );
  const [result, setResult] = useState<PortfolioOptimizationResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      setResult(
        await optimizePortfolio({
          symbols: parseSymbols(symbols),
          startDate: DEFAULT_START,
          endDate: DEFAULT_END,
          objective,
          riskFreeRate: 0.03,
        }),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "组合优化失败。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">组合研究</div>
        <h1 className="panel-title">组合优化</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>标的代码</label>
            <input value={symbols} onChange={(event) => setSymbols(event.target.value)} />
          </div>
          <div className="field-grid">
            <label>优化目标</label>
            <select
              value={objective}
              onChange={(event) => setObjective(event.target.value as typeof objective)}
            >
              <option value="equal_weight">等权配置</option>
              <option value="minimum_variance">最小方差</option>
              <option value="maximum_sharpe">最大夏普</option>
              <option value="risk_parity">风险平价</option>
            </select>
          </div>
          <button className="primary-button" disabled={loading} onClick={submit}>
            优化组合
          </button>
          {loading ? <StateSurface state="loading" title="组合优化运行中。" /> : null}
          {error ? <StateSurface state="error" title="组合优化失败。" detail={error} /> : null}
        </div>
      </article>
      <article className="panel">
        <div className="eyebrow">目标权重</div>
        <h2 className="panel-title">
          {result?.objective ? displayPortfolioObjective(result.objective) : "尚未优化"}
        </h2>
        <MetadataBanner metadata={result?.metadata} />
        <div className="status-list">
          {result?.allocations.length ? (
            result.allocations.map((item) => (
            <div className="status-item" data-status="migrated" key={item.symbol}>
              <div className="status-head">
                <strong>{item.symbol}</strong>
                <span className="status-pill">{(item.weight * 100).toFixed(2)}%</span>
              </div>
            </div>
            ))
          ) : (
            <StateSurface state="empty" title="运行组合优化后查看目标权重。" />
          )}
        </div>
      </article>
    </section>
  );
}
