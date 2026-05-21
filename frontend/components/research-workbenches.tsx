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
  const [prompt, setPrompt] = useState("strong momentum under low price");
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
      setError(caught instanceof Error ? caught.message : "Screener request failed.");
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
      setError(caught instanceof Error ? caught.message : "Screener export failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">Screener</div>
        <h1 className="panel-title">Structured stock screening</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>Universe</label>
            <input value={symbols} onChange={(event) => setSymbols(event.target.value)} />
          </div>
          <div className="field-grid">
            <label>Natural language prompt</label>
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} />
          </div>
          <div className="field-row">
            <div className="field-grid">
              <label>Min change %</label>
              <input value={minChange} onChange={(event) => setMinChange(event.target.value)} />
            </div>
            <div className="field-grid">
              <label>Max price</label>
              <input value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} />
            </div>
          </div>
          <div className="submit-row">
            <button className="primary-button" disabled={loading} onClick={submit}>
              Run screener
            </button>
            <button className="secondary-button" disabled={loading || !result} onClick={exportRows}>
              Export rows
            </button>
          </div>
          {loading ? (
            <StateSurface state="loading" title="Screening request is running." />
          ) : null}
          {error ? <StateSurface state="error" title="Screener request failed." detail={error} /> : null}
        </div>
      </article>

      <article className="panel">
        <div className="eyebrow">Results</div>
        <h2 className="panel-title">Ranked candidates</h2>
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
                <span className="status-pill">Score {item.score.toFixed(2)}</span>
              </div>
              <div className="metric-grid">
                <div className="summary-item">
                  <span className="metric-label">Price</span>
                  <strong>{item.price.toFixed(2)}</strong>
                </div>
                <div className="summary-item">
                  <span className="metric-label">Change</span>
                  <strong>{item.changePercent.toFixed(2)}%</strong>
                </div>
              </div>
            </div>
            ))
          ) : (
            <StateSurface
              state={result ? "empty" : "empty"}
              title={result ? "No candidates matched this screen." : "Run a screen to see candidates."}
              detail={result ? "Applied filters are still visible in the response summary." : undefined}
            />
          )}
        </div>
        {exportResult ? (
          <div className="banner banner-neutral">
            Export ready: {exportResult.rows.length} rows, {exportResult.columns.length} columns.
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
      setError(caught instanceof Error ? caught.message : "Diagnosis request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">Diagnosis</div>
        <h1 className="panel-title">Structured stock diagnosis</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>Symbol</label>
            <input value={symbol} onChange={(event) => setSymbol(event.target.value)} />
          </div>
          <button className="primary-button" disabled={loading} onClick={submit}>
            Generate report
          </button>
          {loading ? <StateSurface state="loading" title="Diagnosis report is running." /> : null}
          {error ? <StateSurface state="error" title="Diagnosis request failed." detail={error} /> : null}
        </div>
      </article>
      <article className="panel">
        <div className="eyebrow">Report</div>
        <h2 className="panel-title">{result?.name || "Awaiting symbol"}</h2>
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
            <StateSurface state="empty" title="Generate a report to inspect structured sections." />
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
      setError(caught instanceof Error ? caught.message : "Factor analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">Factors</div>
        <h1 className="panel-title">Factor analysis</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>Symbol</label>
            <input value={symbol} onChange={(event) => setSymbol(event.target.value)} />
          </div>
          <button className="primary-button" disabled={loading} onClick={submit}>
            Analyze factors
          </button>
          {loading ? <StateSurface state="loading" title="Factor analysis is running." /> : null}
          {error ? <StateSurface state="error" title="Factor analysis failed." detail={error} /> : null}
        </div>
      </article>
      <article className="panel">
        <div className="eyebrow">Ranked IC</div>
        <h2 className="panel-title">{result?.symbol || "No analysis yet"}</h2>
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
            <StateSurface state="empty" title="Run factor analysis to see ranked factors." />
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
      setError(caught instanceof Error ? caught.message : "Portfolio optimization failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workbench-grid">
      <article className="panel">
        <div className="eyebrow">Portfolio</div>
        <h1 className="panel-title">Portfolio optimization</h1>
        <div className="console-form">
          <div className="field-grid">
            <label>Symbols</label>
            <input value={symbols} onChange={(event) => setSymbols(event.target.value)} />
          </div>
          <div className="field-grid">
            <label>Objective</label>
            <select
              value={objective}
              onChange={(event) => setObjective(event.target.value as typeof objective)}
            >
              <option value="equal_weight">Equal weight</option>
              <option value="minimum_variance">Minimum variance</option>
              <option value="maximum_sharpe">Maximum Sharpe</option>
              <option value="risk_parity">Risk parity</option>
            </select>
          </div>
          <button className="primary-button" disabled={loading} onClick={submit}>
            Optimize
          </button>
          {loading ? <StateSurface state="loading" title="Portfolio optimization is running." /> : null}
          {error ? <StateSurface state="error" title="Portfolio optimization failed." detail={error} /> : null}
        </div>
      </article>
      <article className="panel">
        <div className="eyebrow">Allocation</div>
        <h2 className="panel-title">{result?.objective || "No optimization yet"}</h2>
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
            <StateSurface state="empty" title="Run optimization to see target weights." />
          )}
        </div>
      </article>
    </section>
  );
}
