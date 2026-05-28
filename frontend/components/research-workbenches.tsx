"use client";

import { useState } from "react";
import { Download, Play, Stethoscope, BarChart3, Briefcase } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";

import {
  analyzeFactors,
  exportScreener,
  optimizePortfolio,
  runDiagnosis,
  runScreener,
} from "@/lib/api";
import { MetadataState } from "@/components/workbench-layout";
import { displayPortfolioObjective } from "@/lib/display";
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
    <section className="grid gap-6 lg:grid-cols-[1.15fr_minmax(340px,0.85fr)]">
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">条件选股</span>
          <CardTitle className="font-display">结构化股票筛选</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>标的池</Label>
              <Input value={symbols} onChange={(e) => setSymbols(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label>自然语言条件</Label>
              <Textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={3} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-2">
                <Label>最小涨跌幅</Label>
                <Input value={minChange} onChange={(e) => setMinChange(e.target.value)} />
              </div>
              <div className="grid gap-2">
                <Label>最高价格</Label>
                <Input value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
              </div>
            </div>
            <div className="flex items-end gap-3">
              <Button disabled={loading} onClick={submit}>
                <Play className="size-4" />
                运行选股
              </Button>
              <Button variant="outline" disabled={loading || !result} onClick={exportRows}>
                <Download className="size-4" />
                导出结果
              </Button>
            </div>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Skeleton className="size-4 rounded-full" />
                选股请求运行中...
              </div>
            ) : null}
            {error ? (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">筛选结果</span>
          <CardTitle className="font-display">候选标的排序</CardTitle>
        </CardHeader>
        <CardContent>
          <MetadataBanner metadata={result?.metadata} />
          <div className="mt-4 grid gap-3">
            {result?.items.length ? (
              result.items.map((item) => (
                <div key={item.symbol} className="grid gap-3 rounded-lg border border-border bg-card p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-display text-lg font-bold">{item.symbol}</h3>
                      <p className="text-sm text-muted-foreground">{item.name}</p>
                    </div>
                    <Badge variant="secondary">评分 {item.score.toFixed(2)}</Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="grid gap-1 rounded-md bg-muted/50 p-2">
                      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">价格</span>
                      <span className="font-display text-lg font-bold">{item.price.toFixed(2)}</span>
                    </div>
                    <div className="grid gap-1 rounded-md bg-muted/50 p-2">
                      <span className="text-[0.65rem] font-bold uppercase tracking-wider text-primary">涨跌幅</span>
                      <span className="font-display text-lg font-bold">{item.changePercent.toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                {result ? "当前条件没有匹配候选。" : "运行一次选股后查看候选标的。"}
              </div>
            )}
          </div>
          {exportResult ? (
            <Alert className="mt-4">
              <AlertDescription>
                导出已准备：{exportResult.rows.length} 行，{exportResult.columns.length} 列。
              </AlertDescription>
            </Alert>
          ) : null}
        </CardContent>
      </Card>
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

  const toneStyles: Record<string, string> = {
    positive: "border-positive/25 bg-positive-soft",
    warning: "border-warning/25 bg-warning-soft",
    neutral: "bg-muted/50",
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[1.15fr_minmax(340px,0.85fr)]">
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">诊股报告</span>
          <CardTitle className="font-display">结构化股票诊断</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>股票代码</Label>
              <Input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
            </div>
            <Button disabled={loading} onClick={submit}>
              <Stethoscope className="size-4" />
              生成报告
            </Button>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Skeleton className="size-4 rounded-full" />
                诊股报告生成中...
              </div>
            ) : null}
            {error ? (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">报告内容</span>
          <CardTitle className="font-display">{result?.name || "等待输入标的"}</CardTitle>
        </CardHeader>
        <CardContent>
          <MetadataBanner metadata={result?.metadata} />
          <div className="mt-4 grid gap-3">
            {result?.sections.length ? (
              result.sections.map((section) => (
                <div
                  key={section.title}
                  className={"grid gap-2 rounded-lg border border-border p-4 " + (toneStyles[section.tone] || "")}
                >
                  <strong className="text-sm">{section.title}</strong>
                  <p className="text-sm leading-relaxed text-muted-foreground">{section.summary}</p>
                </div>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                生成报告后查看结构化段落。
              </div>
            )}
          </div>
        </CardContent>
      </Card>
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
    <section className="grid gap-6 lg:grid-cols-[1.15fr_minmax(340px,0.85fr)]">
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">因子研究</span>
          <CardTitle className="font-display">因子分析</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>股票代码</Label>
              <Input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
            </div>
            <Button disabled={loading} onClick={submit}>
              <BarChart3 className="size-4" />
              分析因子
            </Button>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Skeleton className="size-4 rounded-full" />
                因子分析运行中...
              </div>
            ) : null}
            {error ? (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">IC 排名</span>
          <CardTitle className="font-display">{result?.symbol || "尚未分析"}</CardTitle>
        </CardHeader>
        <CardContent>
          <MetadataBanner metadata={result?.metadata} />
          <div className="mt-4 grid gap-2">
            {result?.rankedFactors.length ? (
              result.rankedFactors.map((item) => (
                <div key={item.name} className="flex items-center justify-between rounded-lg border border-positive/25 bg-positive-soft p-3">
                  <span className="text-sm font-semibold">{item.name}</span>
                  <Badge variant="secondary">{item.ic.toFixed(3)}</Badge>
                </div>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                运行因子分析后查看排名。
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}

export function PortfolioWorkbench() {
  const [symbols, setSymbols] = useState("000001,600000,300750");
  const [objective, setObjective] = useState<
    "equal_weight" | "minimum_variance" | "maximum_sharpe" | "risk_parity"
  >("maximum_sharpe");
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
    <section className="grid gap-6 lg:grid-cols-[1.15fr_minmax(340px,0.85fr)]">
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">组合研究</span>
          <CardTitle className="font-display">组合优化</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>标的代码</Label>
              <Input value={symbols} onChange={(e) => setSymbols(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label>优化目标</Label>
              <Select value={objective} onValueChange={(v) => setObjective(v as typeof objective)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="equal_weight">等权配置</SelectItem>
                  <SelectItem value="minimum_variance">最小方差</SelectItem>
                  <SelectItem value="maximum_sharpe">最大夏普</SelectItem>
                  <SelectItem value="risk_parity">风险平价</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button disabled={loading} onClick={submit}>
              <Briefcase className="size-4" />
              优化组合
            </Button>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Skeleton className="size-4 rounded-full" />
                组合优化运行中...
              </div>
            ) : null}
            {error ? (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">目标权重</span>
          <CardTitle className="font-display">
            {result?.objective ? displayPortfolioObjective(result.objective) : "尚未优化"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <MetadataBanner metadata={result?.metadata} />
          <div className="mt-4 grid gap-2">
            {result?.allocations.length ? (
              result.allocations.map((item) => (
                <div key={item.symbol} className="flex items-center justify-between rounded-lg border border-positive/25 bg-positive-soft p-3">
                  <span className="text-sm font-semibold">{item.symbol}</span>
                  <Badge variant="secondary">{(item.weight * 100).toFixed(2)}%</Badge>
                </div>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                运行组合优化后查看目标权重。
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
