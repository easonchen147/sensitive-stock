"use client";

import { useEffect, useState } from "react";

import { getBacktestPresets, runBacktests } from "@/lib/api";
import { StateSurface } from "@/components/workbench-layout";
import {
  displayExecutionMode,
  displayText,
  displayTone,
  displayTradeAction,
  displayWorkflowStatus,
} from "@/lib/display";
import {
  applyQuickProfile,
  BACKTEST_QUICK_PROFILES,
  buildBacktestFormSummary,
  buildBacktestPayload,
  formatDecimal,
  formatMetricValue,
  parseSymbolsInput,
  type BacktestFormValues,
  validateBacktestForm,
} from "@/lib/backtests";
import type {
  BacktestAssumption,
  BacktestInsight,
  BacktestPreset,
  BacktestRunResponse,
  BacktestSeriesPoint,
  BacktestSymbolResult,
} from "@/types/api";

const DEFAULT_STRATEGY = `def generate_signals(data, ctx):
    fast_window = int(ctx.params.get("fast_window", 5))
    slow_window = int(ctx.params.get("slow_window", 20))

    close = data["close"]
    fast = ctx.sma(close, fast_window)
    slow = ctx.sma(close, slow_window)

    signal = ctx.new_signal()
    signal[ctx.cross_over(fast, slow)] = 1
    signal[ctx.cross_under(fast, slow)] = 0
    return signal.ffill().fillna(0)
`;

const INITIAL_FORM: BacktestFormValues = {
  symbolsInput: "000001,600000",
  startDate: "2025-01-01",
  endDate: "2025-03-31",
  benchmarkSymbol: "159919",
  strategyMode: "preset",
  strategyPreset: "ma_cross",
  strategyCode: DEFAULT_STRATEGY,
  initialCapital: 100000,
  executionMode: "close",
  positionSize: 1,
  lotSize: 100,
  volumeLimitPct: 0.25,
  tradingFee: 0.0005,
  stampTax: 0.001,
  slippage: 0,
  minCommission: 5,
  transferFeeRate: 0.00002,
  adjust: "qfq",
  stopLoss: 0,
  takeProfit: 0,
  maxDrawdown: 0,
  maxDailyLoss: 0,
  maxPositionSize: 0,
  reduceOnlyAfterRisk: false,
  riskCooldownBars: 0,
  params: {
    fast_window: 5,
    slow_window: 20,
  },
};

const PARAMETER_GROUP_LABELS: Record<string, string> = {
  trend: "趋势参数",
  momentum: "动量参数",
  threshold: "阈值参数",
  breakout: "突破参数",
};

export function BacktestConsole() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [presets, setPresets] = useState<BacktestPreset[]>([]);
  const [result, setResult] = useState<BacktestRunResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadPresets() {
      const items = await getBacktestPresets();
      if (!active || !items.length) {
        return;
      }

      setPresets(items);
      const defaultPreset = items.find((item) => item.id === INITIAL_FORM.strategyPreset) || items[0];
      setForm((current) => ({
        ...current,
        strategyPreset: defaultPreset.id,
        strategyCode: defaultPreset.code,
        params: Object.keys(current.params).length ? current.params : defaultPreset.defaultParams,
      }));
    }

    void loadPresets();
    return () => {
      active = false;
    };
  }, []);

  const currentPreset = presets.find((item) => item.id === form.strategyPreset) || null;
  const symbolCount = parseSymbolsInput(form.symbolsInput).length;
  const validationErrors = validateBacktestForm(form);
  const summaryItems = buildBacktestFormSummary(form, currentPreset?.label);
  const parameterGroups = groupParameterSchema(currentPreset);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (validationErrors.length) {
      setError(validationErrors.join(" / "));
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await runBacktests(buildBacktestPayload(form));
      setResult(response);
      if (!response.results.length && response.failures.length) {
        setError(response.failures.map((item) => `${item.symbol}: ${item.message}`).join(" / "));
      }
    } catch (requestError) {
      const message =
        requestError instanceof Error ? requestError.message : "未知错误，无法完成回测请求。";
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function updateNumberField<K extends keyof BacktestFormValues>(key: K, value: string) {
    setForm((current) => ({
      ...current,
      [key]: Number(value),
    }));
  }

  function updateBooleanField<K extends keyof BacktestFormValues>(key: K, value: boolean) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function applyPreset(presetId: string) {
    const preset = presets.find((item) => item.id === presetId);
    if (!preset) {
      return;
    }

    setForm((current) => ({
      ...current,
      strategyPreset: preset.id,
      strategyCode: preset.code,
      params: { ...preset.defaultParams },
    }));
  }

  function updatePresetParam(name: string, rawValue: string) {
    const schemaItem = currentPreset?.parameterSchema.find((item) => item.name === name);
    const value = schemaItem?.type === "number" ? Number(rawValue) : rawValue;
    setForm((current) => ({
      ...current,
      params: {
        ...current.params,
        [name]: value,
      },
    }));
  }

  return (
    <section className="stack">
      <section className="workbench-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">结构化输入</div>
              <h2 className="panel-title">把输入按研究思路分组，而不是堆成长表单</h2>
              <p className="panel-subtitle">
                市场范围、策略、执行、成本和风险是五组不同的决策。每一组都会在提交前和结果后重复回显，减少“跑完才想起自己设了什么”的情况。
              </p>
            </div>
          </div>

          {error ? <StateSurface state="error" title="回测请求需要处理。" detail={error} /> : null}
          {result && !error ? (
            <StateSurface
              state="ready"
              title="回测响应已返回。"
              detail={`已返回 ${result.results.length} 个标的结果，失败 ${result.failures.length} 个。`}
            />
          ) : null}

          <div className="pill-row">
            {BACKTEST_QUICK_PROFILES.map((profile) => (
              <button
                className="profile-chip"
                key={profile.id}
                type="button"
                onClick={() => setForm((current) => applyQuickProfile(current, profile.id))}
              >
                <span>{profile.label}</span>
                <small>{profile.description}</small>
              </button>
            ))}
          </div>

          <form className="console-form" onSubmit={handleSubmit}>
            <FormSection
              title="市场范围"
              description="先确定标的、时间、复权方式和可选基准。当前仍是单标的批量回测，不是组合级撮合。"
            >
              <div className="field-grid">
                <label htmlFor="symbolsInput">标的代码</label>
                <input
                  id="symbolsInput"
                  value={form.symbolsInput}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, symbolsInput: event.target.value }))
                  }
                  placeholder="000001,600000"
                />
                <span className="field-hint">最多 5 个标的，逗号分隔。</span>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="benchmarkSymbol">基准代码</label>
                  <input
                    id="benchmarkSymbol"
                    value={form.benchmarkSymbol}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, benchmarkSymbol: event.target.value }))
                    }
                    placeholder="可选，例如 159919"
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="adjust">复权方式</label>
                  <select
                    id="adjust"
                    value={form.adjust}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        adjust: event.target.value as "" | "qfq" | "hfq",
                      }))
                    }
                  >
                    <option value="qfq">前复权</option>
                    <option value="hfq">后复权</option>
                    <option value="">不复权</option>
                  </select>
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="startDate">开始日期</label>
                  <input
                    id="startDate"
                    type="date"
                    value={form.startDate}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, startDate: event.target.value }))
                    }
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="endDate">结束日期</label>
                  <input
                    id="endDate"
                    type="date"
                    value={form.endDate}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, endDate: event.target.value }))
                    }
                  />
                </div>
              </div>
            </FormSection>

            <FormSection
              title="策略与参数"
              description="预设模式从后端动态读取参数说明；自定义模式继续遵循策略函数契约。"
            >
              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="strategyMode">策略模式</label>
                  <select
                    id="strategyMode"
                    value={form.strategyMode}
                    onChange={(event) => {
                      const nextMode = event.target.value as "preset" | "custom";
                      setForm((current) => ({
                        ...current,
                        strategyMode: nextMode,
                      }));
                      if (nextMode === "preset" && presets.length) {
                        applyPreset(form.strategyPreset || presets[0].id);
                      }
                    }}
                  >
                    <option value="preset">预设策略</option>
                    <option value="custom">自定义策略</option>
                  </select>
                </div>
                <div className="field-grid">
                  <label htmlFor="strategyPreset">策略预设</label>
                  <select
                    disabled={form.strategyMode !== "preset"}
                    id="strategyPreset"
                    value={form.strategyPreset}
                    onChange={(event) => applyPreset(event.target.value)}
                  >
                    {presets.map((preset) => (
                      <option key={preset.id} value={preset.id}>
                        {preset.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {form.strategyMode === "preset" && currentPreset ? (
                <>
                  <div className="preset-summary">
                    <div className="preset-card" data-active="true">
                      <span className="metric-label">预设摘要</span>
                      <strong>{currentPreset.summary}</strong>
                      <p>{currentPreset.useCase}</p>
                      <small>{currentPreset.riskNotes}</small>
                    </div>
                  </div>

                  {parameterGroups.map(([groupName, items]) => (
                    <div className="parameter-group" key={groupName}>
                      <div className="parameter-group-title">
                        {PARAMETER_GROUP_LABELS[groupName] || groupName}
                      </div>
                      <div className="field-row">
                        {items.map((item) => (
                          <div className="field-grid" key={item.name}>
                            <label htmlFor={`param-${item.name}`}>{item.label}</label>
                            <input
                              id={`param-${item.name}`}
                              max={item.max}
                              min={item.min}
                              step={item.step}
                              type={item.type === "number" ? "number" : "text"}
                              value={String(form.params[item.name] ?? item.default)}
                              onChange={(event) => updatePresetParam(item.name, event.target.value)}
                            />
                            <span className="field-hint">{item.helpText || "参数解释由后端提供。"}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </>
              ) : null}

              <div className="field-grid">
                <label htmlFor="strategyCode">
                  {form.strategyMode === "preset" ? "预设代码预览" : "策略代码"}
                </label>
                <textarea
                  id="strategyCode"
                  readOnly={form.strategyMode === "preset"}
                  value={form.strategyCode}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, strategyCode: event.target.value }))
                  }
                />
              </div>
            </FormSection>

            <FormSection
              title="执行假设"
              description="这部分决定信号何时成交、按多大仓位成交，以及是否贴近 A 股整手交易约束。"
            >
              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="initialCapital">初始资金</label>
                  <input
                    id="initialCapital"
                    type="number"
                    value={form.initialCapital}
                    onChange={(event) => updateNumberField("initialCapital", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="executionMode">成交模式</label>
                  <select
                    id="executionMode"
                    value={form.executionMode}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        executionMode: event.target.value as "close" | "next_open",
                      }))
                    }
                  >
                    <option value="close">当日收盘成交</option>
                    <option value="next_open">次日开盘成交</option>
                  </select>
                  <span className="field-hint">
                    次日开盘成交在最后一根 K 线没有下一日开盘价时会忽略该次信号变化。
                  </span>
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="positionSize">单次仓位</label>
                  <input
                    id="positionSize"
                    max="1"
                    min="0.1"
                    step="0.05"
                    type="number"
                    value={form.positionSize}
                    onChange={(event) => updateNumberField("positionSize", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="lotSize">最小手数</label>
                  <input
                    id="lotSize"
                    step="100"
                    type="number"
                    value={form.lotSize}
                    onChange={(event) => updateNumberField("lotSize", event.target.value)}
                  />
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="volumeLimitPct">成交量限制</label>
                  <input
                    id="volumeLimitPct"
                    max="1"
                    min="0"
                    step="0.01"
                    type="number"
                    value={form.volumeLimitPct}
                    onChange={(event) => updateNumberField("volumeLimitPct", event.target.value)}
                  />
                  <span className="field-hint">限制单次成交不超过当根 K 线成交量的一定比例。</span>
                </div>
                <div className="field-grid">
                  <label>执行说明</label>
                  <div className="submit-note">
                    该参数直接交给 AKQuant，用于模拟容量约束和无法完全成交的情况。
                  </div>
                </div>
              </div>
            </FormSection>

            <FormSection
              title="成本与风控"
              description="回测里最容易被忽略、但最影响真实可用性的部分，不建议默认全设成 0。"
            >
              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="tradingFee">交易佣金</label>
                  <input
                    id="tradingFee"
                    step="0.0001"
                    type="number"
                    value={form.tradingFee}
                    onChange={(event) => updateNumberField("tradingFee", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="stampTax">印花税</label>
                  <input
                    id="stampTax"
                    step="0.0001"
                    type="number"
                    value={form.stampTax}
                    onChange={(event) => updateNumberField("stampTax", event.target.value)}
                  />
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="slippage">滑点</label>
                  <input
                    id="slippage"
                    step="0.0001"
                    type="number"
                    value={form.slippage}
                    onChange={(event) => updateNumberField("slippage", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="minCommission">最低佣金</label>
                  <input
                    id="minCommission"
                    min="0"
                    step="1"
                    type="number"
                    value={form.minCommission}
                    onChange={(event) => updateNumberField("minCommission", event.target.value)}
                  />
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="transferFeeRate">过户费率</label>
                  <input
                    id="transferFeeRate"
                    min="0"
                    step="0.00001"
                    type="number"
                    value={form.transferFeeRate}
                    onChange={(event) => updateNumberField("transferFeeRate", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="stopLoss">止损阈值</label>
                  <input
                    id="stopLoss"
                    step="0.001"
                    type="number"
                    value={form.stopLoss}
                    onChange={(event) => updateNumberField("stopLoss", event.target.value)}
                  />
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="takeProfit">止盈阈值</label>
                  <input
                    id="takeProfit"
                    step="0.001"
                    type="number"
                    value={form.takeProfit}
                    onChange={(event) => updateNumberField("takeProfit", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="maxDrawdown">最大回撤阈值</label>
                  <input
                    id="maxDrawdown"
                    min="0"
                    step="0.001"
                    type="number"
                    value={form.maxDrawdown}
                    onChange={(event) => updateNumberField("maxDrawdown", event.target.value)}
                  />
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="maxDailyLoss">日亏损阈值</label>
                  <input
                    id="maxDailyLoss"
                    min="0"
                    step="100"
                    type="number"
                    value={form.maxDailyLoss}
                    onChange={(event) => updateNumberField("maxDailyLoss", event.target.value)}
                  />
                </div>
                <div className="field-grid">
                  <label htmlFor="maxPositionSize">最大持仓股数</label>
                  <input
                    id="maxPositionSize"
                    min="0"
                    step="100"
                    type="number"
                    value={form.maxPositionSize}
                    onChange={(event) => updateNumberField("maxPositionSize", event.target.value)}
                  />
                </div>
              </div>

              <div className="field-row">
                <div className="field-grid">
                  <label htmlFor="riskCooldownBars">风控冷却周期</label>
                  <input
                    id="riskCooldownBars"
                    min="0"
                    step="1"
                    type="number"
                    value={form.riskCooldownBars}
                    onChange={(event) => updateNumberField("riskCooldownBars", event.target.value)}
                  />
                </div>
                <label className="field-grid" htmlFor="reduceOnlyAfterRisk">
                  风控触发后只减仓
                  <input
                    checked={form.reduceOnlyAfterRisk}
                    id="reduceOnlyAfterRisk"
                    type="checkbox"
                    onChange={(event) =>
                      updateBooleanField("reduceOnlyAfterRisk", event.target.checked)
                    }
                  />
                  <span className="field-hint">触发策略级风控后，不再新增开仓，只允许降低风险暴露。</span>
                </label>
              </div>

              <div className="field-grid">
                <label>请求范围</label>
                <div className="submit-note">
                  当前会发送 {symbolCount || 0} 个标的。多标的是逐标的执行，不是组合级撮合。
                </div>
              </div>
            </FormSection>

            <div className="submit-row">
              <div className="submit-note">
                后端会先校验请求结构，再通过回测适配器执行。前端会保留输入，不会在失败时清空表单。
              </div>
              <button className="primary-button" disabled={loading} type="submit">
                {loading ? "运行中" : "运行回测"}
              </button>
            </div>
          </form>
        </article>

        <aside className="panel">
          <div className="eyebrow">提交复核</div>
          <h2 className="panel-title">提交前快速复核</h2>
          <p className="panel-subtitle">
            左边负责配置，右边负责帮你复核当前请求的核心假设，避免埋头改参数时忽略关键限制。
          </p>

          <div className="summary-list">
            {summaryItems.map((item) => (
              <div className="summary-item" key={item.label}>
                <span className="metric-label">{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>

          {validationErrors.length ? (
            <div className="banner banner-warning">
              {validationErrors.map((item) => (
                <div key={item}>{item}</div>
              ))}
            </div>
          ) : null}

          {currentPreset ? (
            <div className="status-list">
              <div className="status-item" data-status="ready">
                <div className="status-head">
                  <strong>预设重点</strong>
                  <span className="status-pill">{currentPreset.label}</span>
                </div>
                <p>{currentPreset.summary}</p>
                {currentPreset.executionMetadata ? (
                  <p>
                    {currentPreset.executionMetadata.engine} {currentPreset.executionMetadata.engineVersion}
                    {" · "}
                    {currentPreset.executionMetadata.fillPolicies
                      .map((item) => `${item.mode}:${item.priceBasis}/${item.temporal}`)
                      .join(" · ")}
                  </p>
                ) : null}
              </div>
              <div className="status-item" data-status="ready">
                <div className="status-head">
                  <strong>适用场景</strong>
                  <span className="status-pill">说明</span>
                </div>
                <p>{currentPreset.useCase}</p>
              </div>
              <div className="status-item" data-status="limited">
                <div className="status-head">
                  <strong>风险提示</strong>
                  <span className="status-pill">关注</span>
                </div>
                <p>{currentPreset.riskNotes}</p>
              </div>
            </div>
          ) : null}
        </aside>
      </section>

      <article className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">结构化报告</div>
            <h2 className="panel-title">结果不只看收益，也看假设、风险和执行</h2>
            <p className="panel-subtitle">
              输出会分成收益指标、执行假设、相对基准、交易统计、图表和成交记录。这样更适合做研究复盘，而不是只截图一串收益率。
            </p>
          </div>
        </div>

        {loading ? (
          <StateSurface state="loading" title="正在提交回测请求并等待结果返回。" />
        ) : result ? (
          <BacktestResults result={result} />
        ) : (
          <StateSurface
            state="empty"
            title="还没有回测结果。"
            detail="先配置策略与执行假设，提交后这里会展示多标的结果卡、假设摘要、相对基准洞察和最近成交记录。"
          />
        )}
      </article>
    </section>
  );
}

function FormSection({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="form-section">
      <div className="form-section-head">
        <div className="metric-label">{title}</div>
        <p>{description}</p>
      </div>
      {children}
    </section>
  );
}

function BacktestResults({ result }: { result: BacktestRunResponse }) {
  return (
    <div className="results-stack">
      {result.failures.length ? (
        <div className="banner banner-warning">
          {result.failures.map((item) => `${item.symbol}: ${item.message}`).join(" / ")}
        </div>
      ) : null}

      {result.results.map((item) => (
        <article className="result-card" key={item.symbol}>
          <div className="result-header">
            <div>
              <h3>{item.symbol}</h3>
              <p>
                {item.settings.strategyLabel} · {displayExecutionMode(item.settings.executionMode)} ·{" "}
                {displayWorkflowStatus(item.settings.engine || "akquant")} {item.settings.engineVersion || ""}
              </p>
            </div>
            <div className="tag-row">
              <span className="tag-chip">仓位 {(item.settings.positionSize * 100).toFixed(0)}%</span>
              <span className="tag-chip">手数 {item.settings.lotSize}</span>
              <span className="tag-chip">
                容量 {formatMetricValue(item.settings.volumeLimitPct)}
              </span>
              {item.settings.fillPolicy ? (
                <span className="tag-chip">
                  成交 {item.settings.fillPolicy.priceBasis}/{item.settings.fillPolicy.temporal}
                </span>
              ) : null}
              <span className="tag-chip">
                来源 {displayText(item.dataQuality.selectedSource || item.settings.primarySource, "未知")}
              </span>
            </div>
          </div>

          {item.warnings.length ? (
            <div className="banner banner-warning">{item.warnings.join(" / ")}</div>
          ) : null}

          <div className="assumption-grid">
            {item.assumptions.map((assumption) => (
              <AssumptionCard assumption={assumption} key={assumption.label} />
            ))}
          </div>

          <div className="metric-grid">
            <Metric title="总收益" value={formatMetricValue(item.metrics.strategy_total_return)} />
            <Metric title="年化" value={formatMetricValue(item.metrics.annualized_return)} />
            <Metric title="最大回撤" value={formatMetricValue(item.metrics.max_drawdown)} />
            <Metric title="夏普" value={formatDecimal(item.metrics.sharpe)} />
            <Metric title="索提诺" value={formatDecimal(item.metrics.sortino)} />
            <Metric title="卡玛" value={formatDecimal(item.metrics.calmar)} />
            <Metric title="波动率" value={formatMetricValue(item.metrics.volatility)} />
            <Metric title="超额收益" value={formatMetricValue(item.comparison.excess_return)} />
            <Metric title="期末权益" value={formatCurrency(item.tradeStats.endingEquity)} />
            <Metric title="净利润" value={formatCurrency(item.tradeStats.netProfit)} />
            <Metric title="暴露率" value={formatMetricValue(item.tradeStats.exposureRate)} />
            <Metric title="换手" value={formatDecimal(item.tradeStats.turnover)} />
            <Metric title="总成本" value={formatCurrency(item.tradeStats.totalCosts)} />
            <Metric title="平均持有天数" value={formatDecimal(item.tradeStats.averageHoldingDays)} />
          </div>

          <div className="insight-list">
            {item.insights.map((insight) => (
              <InsightCard insight={insight} key={`${insight.title}-${insight.detail}`} />
            ))}
          </div>

          <DiagnosticGrid item={item} />

          <div className="chart-grid">
            <SeriesChart
              title="净值与基准"
              primary={item.series.equity}
              secondary={item.series.benchmark}
            />
            <SeriesChart title="回撤轨迹" primary={item.series.drawdown} variant="drawdown" />
          </div>

          {item.series.monthlyReturns.length ? (
            <div className="monthly-grid">
              {item.series.monthlyReturns.slice(0, 8).map((row) => (
                <div
                  className="monthly-pill"
                  data-tone={row.value >= 0 ? "positive" : "warning"}
                  key={row.month}
                >
                  <span>{row.month}</span>
                  <strong>{formatMetricValue(row.value)}</strong>
                </div>
              ))}
            </div>
          ) : null}

          <table className="trade-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>动作</th>
                <th>原因</th>
                <th>股数</th>
                <th>价格</th>
                <th>费用税费</th>
              </tr>
            </thead>
            <tbody>
              {item.trades.slice(0, 6).map((trade) => (
                <tr key={`${trade.date}-${trade.action}-${trade.price}`}>
                  <td>{trade.date}</td>
                  <td>{displayTradeAction(trade.action)}</td>
                  <td>{displayText(trade.reason)}</td>
                  <td>{trade.shares}</td>
                  <td>{trade.price.toFixed(2)}</td>
                  <td>{(trade.fee + trade.tax).toFixed(2)}</td>
                </tr>
              ))}
              {!item.trades.length ? (
                <tr>
                  <td colSpan={6}>暂无交易记录</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </article>
      ))}
    </div>
  );
}

function DiagnosticGrid({ item }: { item: BacktestSymbolResult }) {
  const dataQuality = item.dataQuality || {};
  const executionQuality = item.executionQuality || {};
  const riskDiagnostics = item.riskDiagnostics || {};
  const engineEvents = item.engineEvents || {
    totalEvents: 0,
    warningCount: 0,
    errorCount: 0,
    byType: {},
    recentTypes: [],
  };

  return (
    <div className="metric-grid">
      <Metric
        title="行情来源"
        value={displayText(dataQuality.selectedSource || dataQuality.primarySource, "未知")}
      />
      <Metric
        title="行情样本"
        value={`${dataQuality.tradingDays || 0} 日 / ${dataQuality.rowCount || 0} 行`}
      />
      <Metric
        title="成交质量"
        value={`${executionQuality.filledOrderCount || 0} 成交 / ${
          executionQuality.rejectedOrderCount || 0
        } 拒单`}
      />
      <Metric
        title="容量限制"
        value={formatMetricValue(executionQuality.volumeLimitPct)}
      />
      <Metric
        title="风险阈值"
        value={formatMetricValue(riskDiagnostics.maxDrawdownLimit)}
      />
      <Metric
        title="实现回撤"
        value={formatMetricValue(riskDiagnostics.realizedMaxDrawdown)}
      />
      <Metric
        title="引擎事件"
        value={`${engineEvents.totalEvents} 条 / 告警 ${engineEvents.warningCount}`}
      />
      <Metric
        title="近期事件"
        value={engineEvents.recentTypes.length ? engineEvents.recentTypes.join(" / ") : "暂无"}
      />
    </div>
  );
}

function Metric({ title, value }: { title: string; value: string }) {
  return (
    <div className="metric-card">
      <span className="metric-label">{title}</span>
      <div className="metric-value">{value}</div>
    </div>
  );
}

function AssumptionCard({ assumption }: { assumption: BacktestAssumption }) {
  return (
    <div className="assumption-card">
      <span className="metric-label">{assumption.label}</span>
      <strong>{assumption.value}</strong>
      <p>{assumption.detail}</p>
    </div>
  );
}

function InsightCard({ insight }: { insight: BacktestInsight }) {
  return (
    <div className="insight-card" data-tone={insight.tone}>
      <div className="status-head">
        <strong>{insight.title}</strong>
        <span className="status-pill">{displayTone(insight.tone)}</span>
      </div>
      <p>{insight.detail}</p>
    </div>
  );
}

function SeriesChart({
  title,
  primary,
  secondary = [],
  variant = "equity",
}: {
  title: string;
  primary: BacktestSeriesPoint[];
  secondary?: BacktestSeriesPoint[];
  variant?: "equity" | "drawdown";
}) {
  if (!primary.length) {
    return <StateSurface state="empty" title="暂无序列数据。" />;
  }

  const primaryValues = primary.map((item) => item.value);
  const secondaryValues = secondary.map((item) => item.value);
  const combined = secondaryValues.length ? [...primaryValues, ...secondaryValues] : primaryValues;
  const maxValue = Math.max(...combined);
  const minValue = Math.min(...combined);
  const domain = maxValue - minValue || 1;

  const primaryPoints = primaryValues
    .map((value, index) => {
      const x = (index / Math.max(primaryValues.length - 1, 1)) * 100;
      const y = 100 - ((value - minValue) / domain) * 100;
      return `${x},${y}`;
    })
    .join(" ");
  const secondaryPoints = secondaryValues
    .map((value, index) => {
      const x = (index / Math.max(secondaryValues.length - 1, 1)) * 100;
      const y = 100 - ((value - minValue) / domain) * 100;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-shell">
      <div className="chart-caption">
        <span>{title}</span>
        <span>{formatDecimal(primaryValues[primaryValues.length - 1], 2)}</span>
      </div>
      <svg className="chart-svg" preserveAspectRatio="none" viewBox="0 0 100 100">
        {secondaryPoints ? (
          <polyline
            fill="none"
            points={secondaryPoints}
            stroke="rgba(38, 56, 74, 0.45)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
          />
        ) : null}
        <polyline
          fill="none"
          points={primaryPoints}
          stroke={variant === "drawdown" ? "rgba(176, 77, 49, 0.95)" : "rgba(28, 111, 94, 0.95)"}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="3"
        />
      </svg>
    </div>
  );
}

function groupParameterSchema(preset: BacktestPreset | null): Array<[string, BacktestPreset["parameterSchema"]]> {
  if (!preset) {
    return [];
  }

  const groups = new Map<string, BacktestPreset["parameterSchema"]>();
  preset.parameterSchema.forEach((item) => {
    const groupName = item.group || "general";
    const existing = groups.get(groupName) || [];
    groups.set(groupName, [...existing, item]);
  });

  return Array.from(groups.entries());
}

function formatCurrency(value?: number | null): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "暂无";
  }
  return `¥${value.toFixed(2)}`;
}
