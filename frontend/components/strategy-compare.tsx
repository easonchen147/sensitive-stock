"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Play } from "lucide-react";
import {
  Line,
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { getBacktestPresets, runBacktests } from "@/lib/api";
import { formatDecimal, formatMetricValue } from "@/lib/backtests";
import type {
  BacktestPreset,
  BacktestRunResponse,
  BacktestSeriesPoint,
  BacktestSymbolResult,
} from "@/types/api";

const COMPARE_COLORS = [
  "#1c6f5e",
  "#b04d31",
  "#2563eb",
  "#9333ea",
];

const COMPARE_METRICS: Array<{
  key: string;
  label: string;
  format: (result: BacktestSymbolResult) => number | null | undefined;
  higherIsBetter: boolean;
}> = [
  {
    key: "total_return",
    label: "总收益率",
    format: (r) => r.metrics.strategy_total_return,
    higherIsBetter: true,
  },
  {
    key: "annualized",
    label: "年化收益率",
    format: (r) => r.metrics.annualized_return,
    higherIsBetter: true,
  },
  {
    key: "max_drawdown",
    label: "最大回撤",
    format: (r) => r.metrics.max_drawdown,
    higherIsBetter: false,
  },
  {
    key: "sharpe",
    label: "夏普比率",
    format: (r) => r.metrics.sharpe,
    higherIsBetter: true,
  },
  {
    key: "win_rate",
    label: "胜率",
    format: (r) => r.tradeStats.winRate,
    higherIsBetter: true,
  },
  {
    key: "trade_count",
    label: "交易次数",
    format: (r) => r.tradeStats.tradeCount,
    higherIsBetter: true,
  },
  {
    key: "avg_trade_return",
    label: "盈亏比",
    format: (r) => r.tradeStats.averageTradeReturn,
    higherIsBetter: true,
  },
];

type CompareItem = {
  presetId: string;
  presetLabel: string;
  result: BacktestSymbolResult | null;
  error: string | null;
};

type EquityPoint = {
  date: string;
  [key: string]: number | string;
};

const today = new Date();
const DEFAULT_END = today.toISOString().slice(0, 10);
const DEFAULT_START = new Date(
  today.getTime() - 365 * 24 * 60 * 60 * 1000,
).toISOString().slice(0, 10);

export function StrategyCompare() {
  const [presets, setPresets] = useState<BacktestPreset[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [symbol, setSymbol] = useState("000001");
  const [startDate, setStartDate] = useState(DEFAULT_START);
  const [endDate, setEndDate] = useState(DEFAULT_END);
  const [initialCapital, setInitialCapital] = useState(100000);
  const [results, setResults] = useState<CompareItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  useEffect(() => {
    let active = true;
    async function load() {
      const items = await getBacktestPresets();
      if (!active || !items.length) return;
      setPresets(items);
      setSelectedIds(items.slice(0, 2).map((p) => p.id));
    }
    void load();
    return () => {
      active = false;
    };
  }, []);

  const togglePreset = useCallback((id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((x) => x !== id);
      }
      if (prev.length >= 4) return prev;
      return [...prev, id];
    });
  }, []);

  const handleRun = useCallback(async () => {
    if (selectedIds.length < 2) {
      setError("请至少选择 2 个策略进行对比。");
      return;
    }
    if (!symbol.trim()) {
      setError("请输入股票代码。");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);
    setProgress({ current: 0, total: selectedIds.length });

    const items: CompareItem[] = [];

    for (let i = 0; i < selectedIds.length; i++) {
      const presetId = selectedIds[i];
      const preset = presets.find((p) => p.id === presetId);
      if (!preset) continue;

      setProgress({ current: i + 1, total: selectedIds.length });

      try {
        const response: BacktestRunResponse = await runBacktests({
          market: {
            symbols: [symbol.trim()],
            startDate,
            endDate,
            adjust: "qfq",
          },
          strategy: {
            mode: "preset",
            presetId: preset.id,
            code: preset.code,
            params: preset.defaultParams,
          },
          execution: {
            mode: "close",
            positionSize: 1,
            lotSize: 100,
            volumeLimitPct: 0.25,
          },
          costs: {
            tradingFee: 0.0005,
            stampTax: 0.001,
            slippage: 0,
            minCommission: 5,
            transferFeeRate: 0.00002,
          },
          risk: {
            stopLoss: 0,
            takeProfit: 0,
            maxDrawdown: 0,
            maxDailyLoss: 0,
            maxPositionSize: 0,
            reduceOnlyAfterRisk: false,
            riskCooldownBars: 0,
          },
          initialCapital,
        });

        const firstResult = response.results.length > 0 ? response.results[0] : null;
        items.push({
          presetId,
          presetLabel: preset.label,
          result: firstResult,
          error: firstResult
            ? null
            : response.failures.length
              ? response.failures.map((f) => f.message).join("; ")
              : "无返回结果",
        });
      } catch (err) {
        items.push({
          presetId,
          presetLabel: preset.label,
          result: null,
          error: err instanceof Error ? err.message : "未知错误",
        });
      }
    }

    setResults(items);
    setLoading(false);
  }, [selectedIds, presets, symbol, startDate, endDate, initialCapital]);

  const equityData = useMemo<EquityPoint[]>(() => {
    if (!results.length) return [];

    const dateMap = new Map<string, EquityPoint>();
    for (const item of results) {
      if (!item.result) continue;
      for (const pt of item.result.series.equity) {
        const existing = dateMap.get(pt.date) || { date: pt.date };
        existing[item.presetId] = pt.value;
        dateMap.set(pt.date, existing);
      }
    }

    return Array.from(dateMap.values()).sort((a, b) =>
      String(a.date).localeCompare(String(b.date)),
    );
  }, [results]);

  const bestWorst = useMemo(() => {
    const map: Record<string, { bestIdx: number; worstIdx: number }> = {};
    for (const metric of COMPARE_METRICS) {
      const values = results.map((item) =>
        item.result ? metric.format(item.result) : null,
      );
      const nums = values.map((v) =>
        typeof v === "number" && !Number.isNaN(v) ? v : null,
      );

      let bestIdx = -1;
      let worstIdx = -1;
      let bestVal: number | null = null;
      let worstVal: number | null = null;

      for (let i = 0; i < nums.length; i++) {
        if (nums[i] === null) continue;
        if (bestVal === null || (metric.higherIsBetter ? nums[i]! > bestVal : nums[i]! < bestVal)) {
          bestVal = nums[i];
          bestIdx = i;
        }
        if (worstVal === null || (metric.higherIsBetter ? nums[i]! < worstVal : nums[i]! > worstVal)) {
          worstVal = nums[i];
          worstIdx = i;
        }
      }

      map[metric.key] = { bestIdx, worstIdx };
    }
    return map;
  }, [results]);

  const chartConfig = useMemo(() => {
    const config: Record<string, { label: string; color: string }> = {};
    results.forEach((item, i) => {
      config[item.presetId] = {
        label: item.presetLabel,
        color: COMPARE_COLORS[i % COMPARE_COLORS.length],
      };
    });
    return config;
  }, [results]);

  return (
    <section className="grid gap-6">
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">
            策略对比
          </span>
          <CardTitle className="font-display">多策略回测对比</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6">
          {error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}

          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div className="grid gap-2">
              <Label htmlFor="compare-symbol">股票代码</Label>
              <Input
                id="compare-symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="000001"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="compare-start">开始日期</Label>
              <Input
                id="compare-start"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="compare-end">结束日期</Label>
              <Input
                id="compare-end"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="compare-capital">初始资金</Label>
              <Input
                id="compare-capital"
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="grid gap-3">
            <div className="flex items-center justify-between">
              <Label>选择策略（2-4 个）</Label>
              <span className="text-xs text-muted-foreground">
                已选 {selectedIds.length}/4
              </span>
            </div>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
              {presets.map((preset) => {
                const checked = selectedIds.includes(preset.id);
                return (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => togglePreset(preset.id)}
                    className={`flex items-start gap-3 rounded-lg border p-3 text-left transition-colors ${
                      checked
                        ? "border-primary bg-primary/5"
                        : "border-border bg-card hover:border-primary/40"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => togglePreset(preset.id)}
                      className="mt-0.5 size-4 rounded border-border"
                    />
                    <div className="grid gap-0.5">
                      <span className="text-sm font-semibold">{preset.label}</span>
                      <span className="text-xs text-muted-foreground">
                        {preset.summary}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-end">
            <Button disabled={loading || selectedIds.length < 2} onClick={handleRun}>
              {loading ? (
                <Skeleton className="size-4 rounded-full" />
              ) : (
                <Play className="size-4" />
              )}
              {loading
                ? `正在回测策略 ${progress.current}/${progress.total}...`
                : "运行对比"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {results.length > 0 ? (
        <>
          <Card>
            <CardHeader>
              <span className="text-xs font-bold uppercase tracking-wider text-primary">
                指标对比
              </span>
              <CardTitle className="font-display">关键指标一览</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="font-semibold">指标</TableHead>
                    {results.map((item, i) => (
                      <TableHead
                        key={item.presetId}
                        className="font-semibold"
                        style={{ color: COMPARE_COLORS[i % COMPARE_COLORS.length] }}
                      >
                        {item.presetLabel}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {COMPARE_METRICS.map((metric) => (
                    <TableRow key={metric.key}>
                      <TableCell className="font-semibold">{metric.label}</TableCell>
                      {results.map((item, i) => {
                        const highlight = bestWorst[metric.key];
                        let className = "";
                        if (highlight) {
                          if (highlight.bestIdx === i && highlight.worstIdx !== i) {
                            className = "bg-positive-soft font-bold text-positive";
                          } else if (
                            highlight.worstIdx === i &&
                            highlight.bestIdx !== i
                          ) {
                            className = "bg-warning-soft font-bold text-warning";
                          }
                        }

                        if (!item.result) {
                          return (
                            <TableCell key={item.presetId} className="text-muted-foreground">
                              {item.error || "失败"}
                            </TableCell>
                          );
                        }

                        const rawValue = metric.format(item.result);
                        const display =
                          typeof rawValue === "number" && !Number.isNaN(rawValue)
                            ? metric.key === "trade_count"
                              ? String(rawValue)
                              : formatMetricValue(rawValue)
                            : "暂无";

                        return (
                          <TableCell key={item.presetId} className={className}>
                            {display}
                          </TableCell>
                        );
                      })}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {equityData.length > 0 ? (
            <Card>
              <CardHeader>
                <span className="text-xs font-bold uppercase tracking-wider text-primary">
                  资金曲线
                </span>
                <CardTitle className="font-display">净值走势对比</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[360px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={equityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.08)" />
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 11 }}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={40}
                      />
                      <YAxis
                        tick={{ fontSize: 11 }}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(v: number) => `${(v / 10000).toFixed(0)}w`}
                        width={50}
                      />
                      <Tooltip
                        formatter={(value) => [
                          `¥${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`,
                          "",
                        ]}
                        labelFormatter={(label) => `日期: ${String(label)}`}
                        contentStyle={{
                          fontSize: 12,
                          borderRadius: 8,
                          border: "1px solid rgba(0,0,0,0.1)",
                        }}
                      />
                      <Legend
                        formatter={(value: string) => {
                          const item = results.find((r) => r.presetId === value);
                          return item?.presetLabel || value;
                        }}
                      />
                      {results.map((item, i) => (
                        <Line
                          key={item.presetId}
                          type="monotone"
                          dataKey={item.presetId}
                          stroke={COMPARE_COLORS[i % COMPARE_COLORS.length]}
                          strokeWidth={2}
                          dot={false}
                          connectNulls
                          name={item.presetId}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2">
            {results.map((item, i) => {
              if (!item.result) {
                return (
                  <Card key={item.presetId}>
                    <CardHeader>
                      <CardTitle
                        className="font-display"
                        style={{ color: COMPARE_COLORS[i % COMPARE_COLORS.length] }}
                      >
                        {item.presetLabel}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Alert variant="destructive">
                        <AlertDescription>{item.error || "回测失败"}</AlertDescription>
                      </Alert>
                    </CardContent>
                  </Card>
                );
              }

              const r = item.result;
              return (
                <Card key={item.presetId}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle
                        className="font-display"
                        style={{ color: COMPARE_COLORS[i % COMPARE_COLORS.length] }}
                      >
                        {item.presetLabel}
                      </CardTitle>
                      <Badge variant="outline">{r.symbol}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{r.settings.strategyLabel}</p>
                  </CardHeader>
                  <CardContent className="grid gap-3">
                    {r.insights.length ? (
                      <div className="grid gap-2">
                        {r.insights.slice(0, 2).map((insight) => (
                          <div
                            key={`${insight.title}-${insight.detail}`}
                            className={`rounded-lg border p-3 ${
                              insight.tone === "positive"
                                ? "border-positive/25 bg-positive-soft"
                                : insight.tone === "warning"
                                  ? "border-warning/25 bg-warning-soft"
                                  : "border-border bg-muted/50"
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <strong className="text-xs">{insight.title}</strong>
                              <Badge variant="secondary" className="text-[0.6rem]">
                                {insight.tone === "positive"
                                  ? "积极"
                                  : insight.tone === "warning"
                                    ? "警示"
                                    : "中性"}
                              </Badge>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {insight.detail}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : null}

                    <div className="grid grid-cols-3 gap-2">
                      <MetricCell title="净利润" value={formatCurrency(r.tradeStats.netProfit)} />
                      <MetricCell title="换手率" value={formatDecimal(r.tradeStats.turnover)} />
                      <MetricCell title="总成本" value={formatCurrency(r.tradeStats.totalCosts)} />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </>
      ) : null}
    </section>
  );
}

function MetricCell({ title, value }: { title: string; value: string }) {
  return (
    <div className="grid gap-0.5 rounded-lg border border-border bg-muted/30 p-2">
      <span className="text-[0.6rem] font-bold uppercase tracking-wider text-primary">
        {title}
      </span>
      <span className="font-display text-xs font-bold">{value}</span>
    </div>
  );
}

function formatCurrency(value?: number | null): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "暂无";
  }
  return `¥${value.toFixed(2)}`;
}
