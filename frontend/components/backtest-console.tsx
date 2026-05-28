"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { SymbolLink } from "@/components/symbol-link";
import { Play } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { getBacktestPresets, runBacktests } from "@/lib/api";
import { NLStrategyEditor } from "@/components/nl-strategy-editor";
import { StrategyCompare } from "@/components/strategy-compare";
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

const today = new Date();
const DEFAULT_END = today.toISOString().slice(0, 10);
const DEFAULT_START = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);

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
  startDate: DEFAULT_START,
  endDate: DEFAULT_END,
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
  const [nlMode, setNlMode] = useState(false);

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
      if (response.results.length) {
        toast.success(`回测完成，共 ${response.results.length} 个策略`);
      }
      if (!response.results.length && response.failures.length) {
        const msg = response.failures.map((item) => `${item.symbol}: ${item.message}`).join(" / ");
        setError(msg);
        toast.error(msg);
      }
    } catch (requestError) {
      const message =
        requestError instanceof Error ? requestError.message : "未知错误，无法完成回测请求。";
      setError(message);
      setResult(null);
      toast.error(message);
    } finally {
      setLoading(false);
    }
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
    <Tabs defaultValue="single" className="grid gap-6">
      <TabsList>
        <TabsTrigger value="single">单策略回测</TabsTrigger>
        <TabsTrigger value="compare">策略对比</TabsTrigger>
      </TabsList>

      <TabsContent value="single">
      <section className="grid gap-6">
        <section className="grid gap-6 lg:grid-cols-[1.15fr_minmax(340px,0.85fr)]">
        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">结构化输入</span>
            <CardTitle className="font-display">策略配置</CardTitle>
          </CardHeader>
          <CardContent>
            {error ? (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
            {result && !error ? (
              <Alert className="mb-4">
                <AlertDescription>
                  已返回 {result.results.length} 个标的结果，失败 {result.failures.length} 个。
                </AlertDescription>
              </Alert>
            ) : null}

            <ToggleGroup type="single" variant="outline" className="mb-4 flex flex-wrap gap-2">
              {BACKTEST_QUICK_PROFILES.map((profile) => (
                <ToggleGroupItem
                  key={profile.id}
                  value={profile.id}
                  onClick={() => setForm((current) => applyQuickProfile(current, profile.id))}
                  className="flex flex-col items-start gap-1 px-3 py-2 h-auto"
                >
                  <span className="text-xs font-bold">{profile.label}</span>
                  <small className="text-[0.6rem] text-muted-foreground">{profile.description}</small>
                </ToggleGroupItem>
              ))}
            </ToggleGroup>

            <form className="grid gap-6" onSubmit={handleSubmit}>
            <div className="grid gap-4">
              <h4 className="text-sm font-bold uppercase tracking-wider text-primary">市场范围</h4>
              <div className="grid gap-2">
                <Label htmlFor="symbolsInput">标的代码</Label>
                <Input
                  id="symbolsInput"
                  value={form.symbolsInput}
                  onChange={(e) => setForm((current) => ({ ...current, symbolsInput: e.target.value }))}
                  placeholder="000001,600000"
                />
                <span className="text-xs text-muted-foreground">最多 5 个标的，逗号分隔。</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="benchmarkSymbol">基准代码</Label>
                  <Input
                    id="benchmarkSymbol"
                    value={form.benchmarkSymbol}
                    onChange={(e) => setForm((current) => ({ ...current, benchmarkSymbol: e.target.value }))}
                    placeholder="可选，例如 159919"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="adjust">复权方式</Label>
                  <Select
                    value={form.adjust}
                    onValueChange={(v) => setForm((current) => ({ ...current, adjust: v as "" | "qfq" | "hfq" }))}
                  >
                    <SelectTrigger id="adjust">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="qfq">前复权</SelectItem>
                      <SelectItem value="hfq">后复权</SelectItem>
                      <SelectItem value="">不复权</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="startDate">开始日期</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={form.startDate}
                    onChange={(e) => setForm((current) => ({ ...current, startDate: e.target.value }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="endDate">结束日期</Label>
                  <Input
                    id="endDate"
                    type="date"
                    value={form.endDate}
                    onChange={(e) => setForm((current) => ({ ...current, endDate: e.target.value }))}
                  />
                </div>
              </div>
            </div>

            <Separator />

            <div className="grid gap-4">
              <h4 className="text-sm font-bold uppercase tracking-wider text-primary">策略与参数</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="strategyMode">策略模式</Label>
                  <Select
                    value={nlMode ? "nl_generate" : form.strategyMode}
                    onValueChange={(v) => {
                      if (v === "nl_generate") {
                        setNlMode(true);
                        setForm((current) => ({ ...current, strategyMode: "custom" }));
                        return;
                      }
                      setNlMode(false);
                      const nextMode = v as "preset" | "custom";
                      setForm((current) => ({ ...current, strategyMode: nextMode }));
                      if (nextMode === "preset" && presets.length) {
                        applyPreset(form.strategyPreset || presets[0].id);
                      }
                    }}
                  >
                    <SelectTrigger id="strategyMode">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="preset">预设策略</SelectItem>
                      <SelectItem value="custom">自定义策略</SelectItem>
                      <SelectItem value="nl_generate">自然语言生成</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="strategyPreset">策略预设</Label>
                  <Select
                    disabled={form.strategyMode !== "preset"}
                    value={form.strategyPreset}
                    onValueChange={(v) => applyPreset(v)}
                  >
                    <SelectTrigger id="strategyPreset">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {presets.map((preset) => (
                        <SelectItem key={preset.id} value={preset.id}>
                          {preset.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {nlMode ? (
                <NLStrategyEditor
                  onApply={(code, params) => {
                    setNlMode(false);
                    setForm((current) => ({
                      ...current,
                      strategyMode: "custom",
                      strategyCode: code,
                      params: { ...params },
                    }));
                  }}
                />
              ) : null}

              {form.strategyMode === "preset" && currentPreset ? (
                <>
                  <div className="rounded-lg border border-primary/25 bg-primary/5 p-4">
                    <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">预设摘要</span>
                    <strong className="mt-1 block text-sm">{currentPreset.summary}</strong>
                    <p className="mt-1 text-xs text-muted-foreground">{currentPreset.useCase}</p>
                    <small className="mt-1 block text-xs text-muted-foreground">{currentPreset.riskNotes}</small>
                  </div>

                  {parameterGroups.map(([groupName, items]) => (
                    <div className="grid gap-3" key={groupName}>
                      <h5 className="text-xs font-bold uppercase tracking-wider text-primary">
                        {PARAMETER_GROUP_LABELS[groupName] || groupName}
                      </h5>
                      <div className="grid grid-cols-2 gap-3">
                        {items.map((item) => (
                          <div className="grid gap-2" key={item.name}>
                            <Label htmlFor={`param-${item.name}`}>{item.label}</Label>
                            <Input
                              id={`param-${item.name}`}
                              max={item.max}
                              min={item.min}
                              step={item.step}
                              type={item.type === "number" ? "number" : "text"}
                              value={String(form.params[item.name] ?? item.default)}
                              onChange={(e) => updatePresetParam(item.name, e.target.value)}
                            />
                            <span className="text-xs text-muted-foreground">{item.helpText || ""}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </>
              ) : null}

              <div className="grid gap-2">
                <Label htmlFor="strategyCode">
                  {form.strategyMode === "preset" ? "预设代码预览" : "策略代码"}
                </Label>
                <Textarea
                  id="strategyCode"
                  readOnly={form.strategyMode === "preset"}
                  value={form.strategyCode}
                  onChange={(e) => setForm((current) => ({ ...current, strategyCode: e.target.value }))}
                  rows={10}
                  className="font-mono text-xs"
                />
              </div>
            </div>

            <Separator />

            <div className="grid gap-4">
              <h4 className="text-sm font-bold uppercase tracking-wider text-primary">执行假设</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="initialCapital">初始资金</Label>
                  <Input
                    id="initialCapital"
                    type="number"
                    value={form.initialCapital}
                    onChange={(e) => setForm((current) => ({ ...current, initialCapital: Number(e.target.value) }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="executionMode">成交模式</Label>
                  <Select
                    value={form.executionMode}
                    onValueChange={(v) => setForm((current) => ({ ...current, executionMode: v as "close" | "next_open" }))}
                  >
                    <SelectTrigger id="executionMode">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="close">当日收盘成交</SelectItem>
                      <SelectItem value="next_open">次日开盘成交</SelectItem>
                    </SelectContent>
                  </Select>
                  <span className="text-xs text-muted-foreground" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="positionSize">单次仓位</Label>
                  <Input
                    id="positionSize"
                    max="1"
                    min="0.1"
                    step="0.05"
                    type="number"
                    value={form.positionSize}
                    onChange={(e) => setForm((current) => ({ ...current, positionSize: Number(e.target.value) }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="lotSize">最小手数</Label>
                  <Input
                    id="lotSize"
                    step="100"
                    type="number"
                    value={form.lotSize}
                    onChange={(e) => setForm((current) => ({ ...current, lotSize: Number(e.target.value) }))}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="volumeLimitPct">成交量限制</Label>
                  <Input
                    id="volumeLimitPct"
                    max="1"
                    min="0"
                    step="0.01"
                    type="number"
                    value={form.volumeLimitPct}
                    onChange={(e) => setForm((current) => ({ ...current, volumeLimitPct: Number(e.target.value) }))}
                  />
                  <span className="text-xs text-muted-foreground">限制单次成交不超过当根 K 线成交量的一定比例。</span>
                </div>
                <div />
              </div>
            </div>

            <Separator />

            <div className="grid gap-4">
              <h4 className="text-sm font-bold uppercase tracking-wider text-primary">成本与风控</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="tradingFee">交易佣金</Label>
                  <Input id="tradingFee" step="0.0001" type="number" value={form.tradingFee}
                    onChange={(e) => setForm((current) => ({ ...current, tradingFee: Number(e.target.value) }))} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="stampTax">印花税</Label>
                  <Input id="stampTax" step="0.0001" type="number" value={form.stampTax}
                    onChange={(e) => setForm((current) => ({ ...current, stampTax: Number(e.target.value) }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="slippage">滑点</Label>
                  <Input id="slippage" step="0.0001" type="number" value={form.slippage}
                    onChange={(e) => setForm((current) => ({ ...current, slippage: Number(e.target.value) }))} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="minCommission">最低佣金</Label>
                  <Input id="minCommission" min="0" step="1" type="number" value={form.minCommission}
                    onChange={(e) => setForm((current) => ({ ...current, minCommission: Number(e.target.value) }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="transferFeeRate">过户费率</Label>
                  <Input id="transferFeeRate" min="0" step="0.00001" type="number" value={form.transferFeeRate}
                    onChange={(e) => setForm((current) => ({ ...current, transferFeeRate: Number(e.target.value) }))} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="stopLoss">止损阈值</Label>
                  <Input id="stopLoss" step="0.001" type="number" value={form.stopLoss}
                    onChange={(e) => setForm((current) => ({ ...current, stopLoss: Number(e.target.value) }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="takeProfit">止盈阈值</Label>
                  <Input id="takeProfit" step="0.001" type="number" value={form.takeProfit}
                    onChange={(e) => setForm((current) => ({ ...current, takeProfit: Number(e.target.value) }))} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="maxDrawdown">最大回撤阈值</Label>
                  <Input id="maxDrawdown" min="0" step="0.001" type="number" value={form.maxDrawdown}
                    onChange={(e) => setForm((current) => ({ ...current, maxDrawdown: Number(e.target.value) }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="maxDailyLoss">日亏损阈值</Label>
                  <Input id="maxDailyLoss" min="0" step="100" type="number" value={form.maxDailyLoss}
                    onChange={(e) => setForm((current) => ({ ...current, maxDailyLoss: Number(e.target.value) }))} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="maxPositionSize">最大持仓股数</Label>
                  <Input id="maxPositionSize" min="0" step="100" type="number" value={form.maxPositionSize}
                    onChange={(e) => setForm((current) => ({ ...current, maxPositionSize: Number(e.target.value) }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-2">
                  <Label htmlFor="riskCooldownBars">风控冷却周期</Label>
                  <Input id="riskCooldownBars" min="0" step="1" type="number" value={form.riskCooldownBars}
                    onChange={(e) => setForm((current) => ({ ...current, riskCooldownBars: Number(e.target.value) }))} />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    checked={form.reduceOnlyAfterRisk}
                    id="reduceOnlyAfterRisk"
                    type="checkbox"
                    className="size-4 rounded border-border"
                    onChange={(e) => setForm((current) => ({ ...current, reduceOnlyAfterRisk: e.target.checked }))}
                  />
                  <Label htmlFor="reduceOnlyAfterRisk" className="text-sm">风控触发后只减仓</Label>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-4">
              <Button disabled={loading} type="submit">
                {loading ? <Skeleton className="size-4 rounded-full" /> : <Play className="size-4" />}
                {loading ? "运行中" : "运行回测"}
              </Button>
            </div>
          </form>
        </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">提交复核</span>
            <CardTitle className="font-display">配置摘要</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {summaryItems.map((item) => (
                <div key={item.label} className="flex items-center justify-between rounded-lg border border-border bg-muted/30 p-3">
                  <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">{item.label}</span>
                  <strong className="text-sm">{item.value}</strong>
                </div>
              ))}
            </div>

            {validationErrors.length ? (
              <Alert variant="destructive" className="mt-4">
                <AlertDescription>
                  {validationErrors.map((item) => (
                    <div key={item}>{item}</div>
                  ))}
                </AlertDescription>
              </Alert>
            ) : null}

            {currentPreset ? (
              <div className="mt-4 grid gap-3">
                <div className="rounded-lg border border-positive/25 bg-positive-soft p-4">
                  <div className="flex items-center justify-between">
                    <strong className="text-sm">预设重点</strong>
                    <Badge variant="secondary">{currentPreset.label}</Badge>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">{currentPreset.summary}</p>
                  {currentPreset.executionMetadata ? (
                    <p className="mt-1 text-xs text-muted-foreground">
                      {currentPreset.executionMetadata.engine} {currentPreset.executionMetadata.engineVersion}
                      {" · "}
                      {currentPreset.executionMetadata.fillPolicies
                        .map((item) => `${item.mode}:${item.priceBasis}/${item.temporal}`)
                        .join(" · ")}
                    </p>
                  ) : null}
                </div>
                <div className="rounded-lg border border-positive/25 bg-positive-soft p-4">
                  <strong className="text-sm">适用场景</strong>
                  <p className="mt-1 text-sm text-muted-foreground">{currentPreset.useCase}</p>
                </div>
                <div className="rounded-lg border border-warning/25 bg-warning-soft p-4">
                  <strong className="text-sm">风险提示</strong>
                  <p className="mt-1 text-sm text-muted-foreground">{currentPreset.riskNotes}</p>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">结构化报告</span>
          <CardTitle className="font-display">回测结果</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Skeleton className="size-4 rounded-full" />
              正在提交回测请求并等待结果返回...
            </div>
          ) : result ? (
            <BacktestResults result={result} />
          ) : (
            <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
              运行回测后查看结果。
            </div>
          )}
        </CardContent>
      </Card>
      </section>
      </TabsContent>

      <TabsContent value="compare">
        <StrategyCompare />
      </TabsContent>
    </Tabs>
  );
}

function MetricTile({ title, value }: { title: string; value: string }) {
  return (
    <div className="grid gap-1 rounded-lg border border-border bg-muted/30 p-3">
      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">{title}</span>
      <span className="font-display text-base font-bold">{value}</span>
    </div>
  );
}

function AssumptionCard({ assumption }: { assumption: BacktestAssumption }) {
  return (
    <div className="grid gap-1 rounded-lg border border-border bg-card p-3">
      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">{assumption.label}</span>
      <strong className="text-sm">{assumption.value}</strong>
      <p className="text-xs text-muted-foreground">{assumption.detail}</p>
    </div>
  );
}

function InsightCard({ insight }: { insight: BacktestInsight }) {
  const toneStyles: Record<string, string> = {
    positive: "border-positive/25 bg-positive-soft",
    warning: "border-warning/25 bg-warning-soft",
    neutral: "bg-muted/50",
  };
  return (
    <div className={`grid gap-2 rounded-lg border border-border p-4 ${toneStyles[insight.tone] || ""}`}>
      <div className="flex items-center justify-between">
        <strong className="text-sm">{insight.title}</strong>
        <Badge variant="secondary">{displayTone(insight.tone)}</Badge>
      </div>
      <p className="text-sm text-muted-foreground">{insight.detail}</p>
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
    return (
      <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
        暂无序列数据。
      </div>
    );
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
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between text-sm">
        <span className="font-semibold">{title}</span>
        <span className="font-display font-bold">{formatDecimal(primaryValues[primaryValues.length - 1], 2)}</span>
      </div>
      <svg className="mt-2 h-32 w-full" preserveAspectRatio="none" viewBox="0 0 100 100">
        {secondaryPoints ? (
          <polyline fill="none" points={secondaryPoints} stroke="rgba(38, 56, 74, 0.45)"
            strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        ) : null}
        <polyline fill="none" points={primaryPoints}
          stroke={variant === "drawdown" ? "rgba(176, 77, 49, 0.95)" : "rgba(28, 111, 94, 0.95)"}
          strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
      </svg>
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
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <MetricTile title="行情来源" value={displayText(dataQuality.selectedSource || dataQuality.primarySource, "未知")} />
      <MetricTile title="行情样本" value={`${dataQuality.tradingDays || 0} 日 / ${dataQuality.rowCount || 0} 行`} />
      <MetricTile title="成交质量" value={`${executionQuality.filledOrderCount || 0} 成交 / ${executionQuality.rejectedOrderCount || 0} 拒单`} />
      <MetricTile title="容量限制" value={formatMetricValue(executionQuality.volumeLimitPct)} />
      <MetricTile title="风险阈值" value={formatMetricValue(riskDiagnostics.maxDrawdownLimit)} />
      <MetricTile title="实现回撤" value={formatMetricValue(riskDiagnostics.realizedMaxDrawdown)} />
      <MetricTile title="引擎事件" value={`${engineEvents.totalEvents} 条 / 告警 ${engineEvents.warningCount}`} />
      <MetricTile title="近期事件" value={engineEvents.recentTypes.length ? engineEvents.recentTypes.join(" / ") : "暂无"} />
    </div>
  );
}

function BacktestResults({ result }: { result: BacktestRunResponse }) {
  return (
    <div className="grid gap-6">
      {result.failures.length ? (
        <Alert variant="destructive">
          <AlertDescription>{result.failures.map((item) => `${item.symbol}: ${item.message}`).join(" / ")}</AlertDescription>
        </Alert>
      ) : null}

      {result.results.map((item) => (
        <Card key={item.symbol}>
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div>
                <SymbolLink symbol={item.symbol} className="text-xs font-bold uppercase tracking-wider text-primary" />
                <CardTitle className="font-display">
                  {item.settings.strategyLabel} · {displayExecutionMode(item.settings.executionMode)}
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  {displayWorkflowStatus(item.settings.engine || "akquant")} {item.settings.engineVersion || ""}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">仓位 {(item.settings.positionSize * 100).toFixed(0)}%</Badge>
                <Badge variant="outline">手数 {item.settings.lotSize}</Badge>
                <Badge variant="outline">容量 {formatMetricValue(item.settings.volumeLimitPct)}</Badge>
                {item.settings.fillPolicy ? (
                  <Badge variant="outline">成交 {item.settings.fillPolicy.priceBasis}/{item.settings.fillPolicy.temporal}</Badge>
                ) : null}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6">
              {item.warnings.length ? (
                <Alert variant="destructive"><AlertDescription>{item.warnings.join(" / ")}</AlertDescription></Alert>
              ) : null}

              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {item.assumptions.map((assumption) => (
                  <AssumptionCard assumption={assumption} key={assumption.label} />
                ))}
              </div>

              <div className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-7">
                <MetricTile title="总收益" value={formatMetricValue(item.metrics.strategy_total_return)} />
                <MetricTile title="年化" value={formatMetricValue(item.metrics.annualized_return)} />
                <MetricTile title="最大回撤" value={formatMetricValue(item.metrics.max_drawdown)} />
                <MetricTile title="夏普" value={formatDecimal(item.metrics.sharpe)} />
                <MetricTile title="索提诺" value={formatDecimal(item.metrics.sortino)} />
                <MetricTile title="卡玛" value={formatDecimal(item.metrics.calmar)} />
                <MetricTile title="波动率" value={formatMetricValue(item.metrics.volatility)} />
                <MetricTile title="超额收益" value={formatMetricValue(item.comparison.excess_return)} />
                <MetricTile title="期末权益" value={formatCurrency(item.tradeStats.endingEquity)} />
                <MetricTile title="净利润" value={formatCurrency(item.tradeStats.netProfit)} />
                <MetricTile title="暴露率" value={formatMetricValue(item.tradeStats.exposureRate)} />
                <MetricTile title="换手" value={formatDecimal(item.tradeStats.turnover)} />
                <MetricTile title="总成本" value={formatCurrency(item.tradeStats.totalCosts)} />
                <MetricTile title="平均持有天数" value={formatDecimal(item.tradeStats.averageHoldingDays)} />
              </div>

              <div className="grid gap-3">
                {item.insights.map((insight) => (
                  <InsightCard insight={insight} key={`${insight.title}-${insight.detail}`} />
                ))}
              </div>

              <DiagnosticGrid item={item} />

              <div className="grid gap-4 md:grid-cols-2">
                <SeriesChart title="净值与基准" primary={item.series.equity} secondary={item.series.benchmark} />
                <SeriesChart title="回撤轨迹" primary={item.series.drawdown} variant="drawdown" />
              </div>

              {item.series.monthlyReturns.length ? (
                <div className="grid grid-cols-4 gap-2 md:grid-cols-8">
                  {item.series.monthlyReturns.slice(0, 8).map((row) => (
                    <div key={row.month} className={`grid gap-1 rounded-lg border p-2 text-center ${
                      row.value >= 0 ? "border-positive/25 bg-positive-soft" : "border-warning/25 bg-warning-soft"
                    }`}>
                      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">{row.month}</span>
                      <strong className="font-display text-sm">{formatMetricValue(row.value)}</strong>
                    </div>
                  ))}
                </div>
              ) : null}

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>日期</TableHead>
                    <TableHead>动作</TableHead>
                    <TableHead>原因</TableHead>
                    <TableHead>股数</TableHead>
                    <TableHead>价格</TableHead>
                    <TableHead>费用税费</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {item.trades.slice(0, 6).map((trade) => (
                    <TableRow key={`${trade.date}-${trade.action}-${trade.price}`}>
                      <TableCell>{trade.date}</TableCell>
                      <TableCell>{displayTradeAction(trade.action)}</TableCell>
                      <TableCell>{displayText(trade.reason)}</TableCell>
                      <TableCell>{trade.shares}</TableCell>
                      <TableCell>{trade.price.toFixed(2)}</TableCell>
                      <TableCell>{(trade.fee + trade.tax).toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                  {!item.trades.length ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">暂无交易记录</TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      ))}
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
