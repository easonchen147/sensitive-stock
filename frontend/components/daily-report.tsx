"use client";

import { useCallback, useEffect, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { runDailyAnalysis, getLatestDailyReport, getDailyHistory } from "@/lib/api";
import type { DailyReport } from "@/types/api";
import {
  AlertTriangle,
  Calendar,
  ChevronDown,
  ChevronUp,
  Loader2,
  RefreshCw,
  Sparkles,
} from "lucide-react";

function formatPercent(value: number) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function changeColor(value: number) {
  if (value > 0) return "text-positive";
  if (value < 0) return "text-negative";
  return "text-muted-foreground";
}

function PickBadge({ score }: { score: number }) {
  if (score >= 80) {
    return <Badge className="bg-positive/15 text-positive">{score}</Badge>;
  }
  if (score >= 60) {
    return <Badge variant="secondary">{score}</Badge>;
  }
  return <Badge variant="outline">{score}</Badge>;
}

export function DailyReportView() {
  const [report, setReport] = useState<DailyReport | null>(null);
  const [history, setHistory] = useState<DailyReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const fetchLatest = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getLatestDailyReport();
      setReport(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "获取最新报告失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRun = useCallback(async () => {
    setRunning(true);
    setError(null);
    try {
      const data = await runDailyAnalysis();
      setReport(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "运行分析失败";
      setError(message);
    } finally {
      setRunning(false);
    }
  }, []);

  const toggleHistory = useCallback(async () => {
    if (!showHistory && history.length === 0) {
      setHistoryLoading(true);
      try {
        const data = await getDailyHistory(10);
        setHistory(data.items ?? []);
      } catch {
        // silently ignore history errors
      } finally {
        setHistoryLoading(false);
      }
    }
    setShowHistory((prev) => !prev);
  }, [showHistory, history.length]);

  useEffect(() => {
    fetchLatest();
  }, [fetchLatest]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Calendar className="size-5 text-primary" />
          <div>
            <h2 className="font-display text-2xl font-bold tracking-tight">每日复盘</h2>
            {report?.date && (
              <p className="text-sm text-muted-foreground">报告日期：{report.date}</p>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchLatest} disabled={loading}>
            <RefreshCw className={`mr-2 size-4 ${loading ? "animate-spin" : ""}`} />
            刷新
          </Button>
          <Button size="sm" onClick={handleRun} disabled={running}>
            {running ? (
              <Loader2 className="mr-2 size-4 animate-spin" />
            ) : (
              <Sparkles className="mr-2 size-4" />
            )}
            运行分析
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="size-4" />
          <AlertTitle>请求失败</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Loading skeleton */}
      {loading && !report && (
        <div className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      )}

      {report && (
        <>
          {/* Market Summary */}
          <Card>
            <CardHeader>
              <CardTitle>市场总结</CardTitle>

            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {report.marketSummary}
              </p>
            </CardContent>
          </Card>

          {/* Top Picks */}
          {report.topPicks.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>精选推荐</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>代码</TableHead>
                      <TableHead>名称</TableHead>
                      <TableHead className="text-center">评分</TableHead>
                      <TableHead className="text-right">价格</TableHead>
                      <TableHead className="text-right">涨跌幅</TableHead>
                      <TableHead>理由</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {report.topPicks.map((pick) => (
                      <TableRow key={pick.symbol}>
                        <TableCell className="font-mono font-bold">
                          {pick.symbol}
                        </TableCell>
                        <TableCell>{pick.name}</TableCell>
                        <TableCell className="text-center">
                          <PickBadge score={pick.score} />
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {pick.price.toFixed(2)}
                        </TableCell>
                        <TableCell className={`text-right font-mono ${changeColor(pick.changePercent)}`}>
                          {formatPercent(pick.changePercent)}
                        </TableCell>
                        <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                          {pick.reason}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {/* Sector Analysis */}
          {report.sectorAnalysis.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>板块分析</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {report.sectorAnalysis.map((item) => (
                    <div
                      key={item.sector}
                      className="flex items-start gap-4 rounded-lg border border-border p-3"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="font-semibold">{item.sector}</p>
                        <p className="text-sm text-muted-foreground">{item.trend}</p>
                      </div>
                      <Badge variant="outline" className="shrink-0">
                        {item.recommendation}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Risk Warnings */}
          {report.riskWarnings.length > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="size-4" />
              <AlertTitle>风险提示</AlertTitle>
              <AlertDescription>
                <ul className="list-inside list-disc space-y-1">
                  {report.riskWarnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {/* AI Insights */}
          {report.aiInsights && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="size-4 text-primary" />
                  AI 洞察
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {report.aiInsights}
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* History */}
      <Card>
        <CardHeader>
          <button
            onClick={toggleHistory}
            className="flex w-full items-center justify-between text-left"
          >
            <CardTitle>历史报告</CardTitle>
            {showHistory ? (
              <ChevronUp className="size-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="size-4 text-muted-foreground" />
            )}
          </button>
        </CardHeader>
        {showHistory && (
          <CardContent>
            {historyLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : history.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无历史报告。</p>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <div
                    key={item.date}
                    className="flex items-center gap-4 rounded-lg border border-border p-3"
                  >
                    <Calendar className="size-4 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold">{item.date}</p>
                      <p className="truncate text-sm text-muted-foreground">
                        {item.marketSummary}
                      </p>
                    </div>
                    <div className="flex shrink-0 gap-2">
                      <Badge variant="secondary">
                        {item.topPicks.length} 推荐
                      </Badge>
                      {item.riskWarnings.length > 0 && (
                        <Badge variant="destructive">
                          {item.riskWarnings.length} 风险
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
