"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SymbolLink } from "@/components/symbol-link";
import { Download, Play, Stethoscope, BarChart3, Briefcase, AlertTriangle, Sparkles, MessageSquareText, ArrowUpDown } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";

import {
  analyzeFactors,
  exportScreener,
  getStockDetail,
  optimizePortfolio,
  runDiagnosis,
  runScreener,
} from "@/lib/api";
import { KlineChart } from "@/components/kline-chart";
import { MetadataState } from "@/components/workbench-layout";
import { displayPortfolioObjective } from "@/lib/display";
import type {
  CapabilityMetadata,
  DiagnosisAIResponse,
  FactorAnalysisResponse,
  PortfolioOptimizationResponse,
  ScreenerExportResponse,
  ScreenerRunResponse,
  StockDetail,
} from "@/types/api";

const today = new Date();
const DEFAULT_END = today.toISOString().slice(0, 10);
const DEFAULT_START = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);

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
  const router = useRouter();

  const [symbols, setSymbols] = useState("000001,600000,300750,000858");
  const [prompt, setPrompt] = useState("低价区间内保持强势动量");
  const [minChange, setMinChange] = useState("0");
  const [maxPrice, setMaxPrice] = useState("80");
  const [sector, setSector] = useState("");
  const [minPE, setMinPE] = useState("");
  const [maxPE, setMaxPE] = useState("");
  const [minMarketCap, setMinMarketCap] = useState("");
  const [maxMarketCap, setMaxMarketCap] = useState("");
  const [minVolumeRatio, setMinVolumeRatio] = useState("");
  const [minTurnover, setMinTurnover] = useState("");
  const [maxTurnover, setMaxTurnover] = useState("");
  const [result, setResult] = useState<ScreenerRunResponse | null>(null);
  const [exportResult, setExportResult] = useState<ScreenerExportResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [sortKey, setSortKey] = useState<"symbol" | "name" | "price" | "changePercent" | "score">("score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  function toggleSort(key: typeof sortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "symbol" || key === "name" ? "asc" : "desc");
    }
  }

  const sortedItems = result
    ? [...result.items].sort((a, b) => {
        const av = a[sortKey];
        const bv = b[sortKey];
        if (typeof av === "string" && typeof bv === "string") {
          return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
        }
        const an = av as number;
        const bn = bv as number;
        return sortDir === "asc" ? an - bn : bn - an;
      })
    : [];

  const payload = {
    universe: parseSymbols(symbols),
    prompt,
    filters: {
      minChangePercent: Number(minChange),
      maxPrice: Number(maxPrice),
      sectors: sector ? [sector] : undefined,
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

  function SortHeader({ label, columnKey }: { label: string; columnKey: typeof sortKey }) {
    return (
      <button
        type="button"
        className="inline-flex items-center gap-1"
        onClick={() => toggleSort(columnKey)}
      >
        {label}
        <ArrowUpDown className="size-3 text-muted-foreground" />
      </button>
    );
  }

  const SECTOR_OPTIONS = ["金融", "科技", "医药", "消费", "能源", "制造"];

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
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-2">
                <Label>行业</Label>
                <Select value={sector} onValueChange={setSector}>
                  <SelectTrigger>
                    <SelectValue placeholder="全部行业" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部行业</SelectItem>
                    {SECTOR_OPTIONS.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label>最小量比</Label>
                <Input value={minVolumeRatio} onChange={(e) => setMinVolumeRatio(e.target.value)} placeholder="如 1.5" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-2">
                <Label>最小 PE</Label>
                <Input value={minPE} onChange={(e) => setMinPE(e.target.value)} placeholder="如 5" />
              </div>
              <div className="grid gap-2">
                <Label>最大 PE</Label>
                <Input value={maxPE} onChange={(e) => setMaxPE(e.target.value)} placeholder="如 50" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-2">
                <Label>最小市值（亿）</Label>
                <Input value={minMarketCap} onChange={(e) => setMinMarketCap(e.target.value)} placeholder="如 100" />
              </div>
              <div className="grid gap-2">
                <Label>最大市值（亿）</Label>
                <Input value={maxMarketCap} onChange={(e) => setMaxMarketCap(e.target.value)} placeholder="如 5000" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-2">
                <Label>最小换手率（%）</Label>
                <Input value={minTurnover} onChange={(e) => setMinTurnover(e.target.value)} placeholder="如 1" />
              </div>
              <div className="grid gap-2">
                <Label>最大换手率（%）</Label>
                <Input value={maxTurnover} onChange={(e) => setMaxTurnover(e.target.value)} placeholder="如 15" />
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
          <CardTitle className="font-display">筛选结果</CardTitle>
        </CardHeader>
        <CardContent>
          <MetadataBanner metadata={result?.metadata} />
          <div className="mt-4">
            {sortedItems.length ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead><SortHeader label="代码" columnKey="symbol" /></TableHead>
                    <TableHead><SortHeader label="名称" columnKey="name" /></TableHead>
                    <TableHead><SortHeader label="价格" columnKey="price" /></TableHead>
                    <TableHead><SortHeader label="涨跌幅" columnKey="changePercent" /></TableHead>
                    <TableHead><SortHeader label="评分" columnKey="score" /></TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedItems.map((item) => (
                    <TableRow key={item.symbol}>
                      <TableCell><SymbolLink symbol={item.symbol} className="font-semibold" /></TableCell>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.price.toFixed(2)}</TableCell>
                      <TableCell>
                        <span className={item.changePercent >= 0 ? "text-positive" : "text-negative"}>
                          {item.changePercent >= 0 ? "+" : ""}{item.changePercent.toFixed(2)}%
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">{item.score.toFixed(2)}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/stocks/${item.symbol}`)}
                          >
                            查看详情
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/backtests?symbol=${item.symbol}`)}
                          >
                            运行回测
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                {result ? "当前条件没有匹配候选。" : "运行选股查看结果。"}
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
  const router = useRouter();
  const [symbol, setSymbol] = useState("000001");
  const [startDate, setStartDate] = useState(DEFAULT_START);
  const [endDate, setEndDate] = useState(DEFAULT_END);
  const [result, setResult] = useState<DiagnosisAIResponse | null>(null);
  const [stockDetail, setStockDetail] = useState<StockDetail | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    setResult(null);
    setStockDetail(null);
    try {
      const [diagnosis, detail] = await Promise.all([
        runDiagnosis({
          symbol,
          startDate,
          endDate,
          includeNews: true,
        }) as Promise<DiagnosisAIResponse>,
        getStockDetail(symbol),
      ]);
      setResult(diagnosis);
      setStockDetail(detail);
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

  const toneBadgeVariant: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
    positive: "default",
    warning: "destructive",
    neutral: "secondary",
  };

  function formatPercent(value: number | null | undefined): string {
    if (value == null) return "--";
    return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
  }

  function formatNumber(value: number | null | undefined, fractionDigits = 2): string {
    if (value == null) return "--";
    return value.toLocaleString("zh-CN", { minimumFractionDigits: fractionDigits, maximumFractionDigits: fractionDigits });
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[0.9fr_minmax(360px,1.1fr)]">
      {/* Left panel: inputs */}
      <Card>
        <CardHeader>
          <span className="text-xs font-bold uppercase tracking-wider text-primary">AI 诊股</span>
          <CardTitle className="font-display">增强版股票诊断</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>股票代码</Label>
              <Input
                placeholder="例如 000001"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-2">
                <Label>开始日期</Label>
                <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </div>
              <div className="grid gap-2">
                <Label>结束日期</Label>
                <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              </div>
            </div>
            <Button disabled={loading || !symbol.trim()} onClick={submit}>
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

      {/* Right panel: diagnosis results */}
      <div className="grid gap-4">
        {/* Stock info header */}
        {stockDetail && !stockDetail.error ? (
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-display text-xl font-bold">{stockDetail.name || symbol}</h3>
                  <p className="text-sm text-muted-foreground">{symbol}{stockDetail.industry ? ` · ${stockDetail.industry}` : ""}</p>
                </div>
                {stockDetail.changePercent != null ? (
                  <Badge variant={stockDetail.changePercent >= 0 ? "default" : "destructive"}>
                    {formatPercent(stockDetail.changePercent)}
                  </Badge>
                ) : null}
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
                {[
                  { label: "最新价", value: formatNumber(stockDetail.price) },
                  { label: "今开", value: formatNumber(stockDetail.open) },
                  { label: "最高", value: formatNumber(stockDetail.high) },
                  { label: "最低", value: formatNumber(stockDetail.low) },
                  { label: "成交量", value: stockDetail.volume != null ? `${(stockDetail.volume / 10000).toFixed(0)}万` : "--" },
                  { label: "换手率", value: stockDetail.turnoverRate != null ? `${stockDetail.turnoverRate.toFixed(2)}%` : "--" },
                  { label: "市盈率", value: stockDetail.pe != null ? stockDetail.pe.toFixed(2) : "--" },
                  { label: "市净率", value: stockDetail.pb != null ? stockDetail.pb.toFixed(2) : "--" },
                ].map((item) => (
                  <div key={item.label} className="grid gap-0.5 rounded-md bg-muted/50 p-2">
                    <span className="text-[0.6rem] font-bold uppercase tracking-wider text-muted-foreground">{item.label}</span>
                    <span className="font-display text-sm font-semibold">{item.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : null}

        {/* Kline chart */}
        {result ? (
          <Card>
            <CardHeader>
              <span className="text-xs font-bold uppercase tracking-wider text-primary">K 线走势</span>
              <CardTitle className="font-display text-base">价格与成交量</CardTitle>
            </CardHeader>
            <CardContent>
              <KlineChart symbol={symbol} height={320} />
            </CardContent>
          </Card>
        ) : null}

        {/* Technical scores grid */}
        {result?.technicalScores?.indicators.length ? (
          <Card>
            <CardHeader>
              <span className="text-xs font-bold uppercase tracking-wider text-primary">技术评分</span>
              <CardTitle className="font-display text-base">
                综合评分 {result.technicalScores.composite.toFixed(1)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {result.technicalScores.indicators.map((item) => {
                  const cardTone = toneStyles[item.tone] || toneStyles.neutral;
                  return (
                    <div key={item.name} className={`grid gap-1 rounded-lg border border-border p-3 ${cardTone}`}>
                      <span className="text-[0.6rem] font-bold uppercase tracking-wider text-muted-foreground">{item.label}</span>
                      <span className="font-display text-lg font-bold">{typeof item.value === "number" ? item.value.toFixed(2) : item.value}</span>
                      {item.score != null ? (
                        <span className="text-xs text-muted-foreground">评分 {item.score.toFixed(1)}</span>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ) : null}

        {/* Diagnosis sections */}
        {result ? (
          <Card>
            <CardHeader>
              <span className="text-xs font-bold uppercase tracking-wider text-primary">诊断段落</span>
              <CardTitle className="font-display text-base">{result.name || symbol} · 结构化分析</CardTitle>
            </CardHeader>
            <CardContent>
              <MetadataBanner metadata={result.metadata} />
              <div className="mt-4 grid gap-3">
                {result.sections.length ? (
                  result.sections.map((section) => (
                    <div
                      key={section.title}
                      className={"grid gap-2 rounded-lg border border-border p-4 " + (toneStyles[section.tone] || "")}
                    >
                      <div className="flex items-center gap-2">
                        <Badge variant={toneBadgeVariant[section.tone] || "secondary"}>{section.tone === "positive" ? "积极" : section.tone === "warning" ? "风险" : "中性"}</Badge>
                        <strong className="text-sm">{section.title}</strong>
                      </div>
                      <p className="text-sm leading-relaxed text-muted-foreground">{section.summary}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                    本次诊断未生成段落内容。
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ) : null}

        {/* AI analysis */}
        {result?.aiAnalysis ? (
          <Card>
            <CardHeader>
              <span className="text-xs font-bold uppercase tracking-wider text-primary flex items-center gap-1">
                <Sparkles className="size-3" />
                AI 洞察
              </span>
              <CardTitle className="font-display text-base">智能分析摘要</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{result.aiAnalysis}</p>
            </CardContent>
          </Card>
        ) : null}

        {/* Risk notes */}
        {result?.riskNotes.length ? (
          <Alert variant="destructive">
            <AlertTriangle className="size-4" />
            <AlertDescription>
              <div className="grid gap-1">
                <span className="font-semibold">风险提示</span>
                <ul className="list-inside list-disc space-y-1">
                  {result.riskNotes.map((note, idx) => (
                    <li key={idx} className="text-sm">{note}</li>
                  ))}
                </ul>
              </div>
            </AlertDescription>
          </Alert>
        ) : null}

        {/* Ask AI button */}
        {result ? (
          <Button
            variant="outline"
            className="w-full"
            onClick={() => router.push(`/qa?symbol=${encodeURIComponent(symbol)}`)}
          >
            <MessageSquareText className="size-4" />
            追问 AI · 深入了解 {stockDetail?.name || symbol}
          </Button>
        ) : null}

        {/* Empty state */}
        {!result && !loading && !error ? (
          <Card>
            <CardContent className="flex min-h-[200px] items-center justify-center">
              <p className="text-sm text-muted-foreground">输入股票代码生成诊断报告。</p>
            </CardContent>
          </Card>
        ) : null}
      </div>
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
          <CardTitle className="font-display">{result?.symbol || "分析结果"}</CardTitle>
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
                运行分析查看结果。
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
            {result?.objective ? displayPortfolioObjective(result.objective) : "优化结果"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <MetadataBanner metadata={result?.metadata} />
          <div className="mt-4 grid gap-2">
            {result?.allocations.length ? (
              result.allocations.map((item) => (
                <div key={item.symbol} className="flex items-center justify-between rounded-lg border border-positive/25 bg-positive-soft p-3">
                  <SymbolLink symbol={item.symbol} className="text-sm font-semibold" />
                  <Badge variant="secondary">{(item.weight * 100).toFixed(2)}%</Badge>
                </div>
              ))
            ) : (
              <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                运行优化查看结果。
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
