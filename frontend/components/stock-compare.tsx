"use client";

import { useCallback, useState } from "react";
import { getStockCompare } from "@/lib/api";
import type { StockCompareItem, StockCompareResponse } from "@/types/api";
import { SymbolLink } from "@/components/symbol-link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2 } from "lucide-react";

type CompareMode = "best" | "worst" | null;

function formatNumber(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return "--";
  return value.toFixed(decimals);
}

function formatMarketCap(value: number | null | undefined): string {
  if (value === null || value === undefined) return "--";
  if (value >= 1e8) return `${(value / 1e8).toFixed(0)}亿`;
  if (value >= 1e4) return `${(value / 1e4).toFixed(0)}万`;
  return value.toFixed(0);
}

function getHighlightClass(
  values: (number | null)[],
  index: number,
  mode: "higherBetter" | "lowerBetter",
): string {
  const validValues = values
    .map((v, i) => ({ value: v, index: i }))
    .filter((v) => v.value !== null) as { value: number; index: number }[];

  if (validValues.length < 2) return "";

  const isBest =
    mode === "higherBetter"
      ? validValues.every((v) => (values[index] ?? -Infinity) >= v.value)
      : validValues.every((v) => (values[index] ?? Infinity) <= v.value);

  const isWorst =
    mode === "higherBetter"
      ? validValues.every((v) => (values[index] ?? Infinity) <= v.value)
      : validValues.every((v) => (values[index] ?? -Infinity) >= v.value);

  if (isBest) return "text-positive font-semibold";
  if (isWorst) return "text-negative font-semibold";
  return "";
}

interface CompareRow {
  label: string;
  key: string;
  format: (v: number | null) => string;
  mode: "higherBetter" | "lowerBetter";
}

const fundamentalRows: CompareRow[] = [
  { label: "最新价", key: "price", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "涨跌幅%", key: "changePercent", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "市盈率(PE)", key: "pe", format: (v) => formatNumber(v, 2), mode: "lowerBetter" },
  { label: "市净率(PB)", key: "pb", format: (v) => formatNumber(v, 2), mode: "lowerBetter" },
  { label: "总市值(亿)", key: "marketCap", format: formatMarketCap, mode: "higherBetter" },
  { label: "换手率%", key: "turnoverRate", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "量比", key: "volumeRatio", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "60日最高", key: "high52w", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "60日最低", key: "low52w", format: (v) => formatNumber(v, 2), mode: "lowerBetter" },
];

const technicalRows: CompareRow[] = [
  { label: "MA5", key: "ma5", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "MA10", key: "ma10", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "MA20", key: "ma20", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "MA60", key: "ma60", format: (v) => formatNumber(v, 2), mode: "higherBetter" },
  { label: "RSI14", key: "rsi14", format: (v) => formatNumber(v, 1), mode: "higherBetter" },
  { label: "MACD DIF", key: "macdDif", format: (v) => formatNumber(v, 4), mode: "higherBetter" },
  { label: "MACD DEA", key: "macdDea", format: (v) => formatNumber(v, 4), mode: "higherBetter" },
  { label: "MACD 柱", key: "macdHistogram", format: (v) => formatNumber(v, 4), mode: "higherBetter" },
];

function CompareTable({
  items,
  rows,
  sectionLabel,
}: {
  items: StockCompareItem[];
  rows: CompareRow[];
  sectionLabel: string;
}) {
  return (
    <div className="mb-6">
      <h3 className="mb-3 text-sm font-bold text-ink">{sectionLabel}</h3>
      <div className="overflow-x-auto rounded-lg border border-line">
        <Table>
          <TableHeader>
            <TableRow className="bg-surface-muted">
              <TableHead className="w-32 font-bold text-ink">指标</TableHead>
              {items.map((item) => (
                <TableHead key={item.symbol} className="min-w-[120px] text-center font-bold text-ink">
                  <SymbolLink symbol={item.symbol} name={item.name} />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.key}>
                <TableCell className="font-medium text-muted">{row.label}</TableCell>
                {items.map((item, index) => {
                  const values = items.map(
                    (i) => (i as unknown as Record<string, unknown>)[row.key] as number | null,
                  );
                  const value = values[index];
                  const highlight = getHighlightClass(values, index, row.mode);
                  return (
                    <TableCell key={item.symbol} className={`text-center tabular-nums ${highlight}`}>
                      {row.format(value)}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

export function StockCompareView() {
  const [inputValue, setInputValue] = useState("");
  const [result, setResult] = useState<StockCompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = useCallback(async () => {
    const symbols = inputValue
      .split(/[,，\s]+/)
      .map((s) => s.trim())
      .filter(Boolean);

    if (symbols.length < 2) {
      setError("请至少输入 2 个股票代码，用逗号分隔");
      return;
    }
    if (symbols.length > 5) {
      setError("最多支持 5 个股票代码对比");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await getStockCompare(symbols);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "请求失败，请重试");
    } finally {
      setLoading(false);
    }
  }, [inputValue]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        handleCompare();
      }
    },
    [handleCompare],
  );

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            股票对比
            <Badge variant="secondary" className="text-xs">
              2-5 只
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Input
              placeholder="输入股票代码，如 000001,600000,000858"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 font-mono"
            />
            <Button onClick={handleCompare} disabled={loading}>
              {loading ? <Loader2 className="mr-2 size-4 animate-spin" /> : null}
              对比
            </Button>
          </div>
          {error && <p className="mt-2 text-sm text-negative">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <>
          {result.degraded && (
            <div className="rounded-lg border border-warning/30 bg-warning-soft px-4 py-2 text-sm text-warning">
              部分数据获取异常，结果可能不完整。
            </div>
          )}
          <CompareTable items={result.items} rows={fundamentalRows} sectionLabel="基本面" />
          <CompareTable items={result.items} rows={technicalRows} sectionLabel="技术面" />
        </>
      )}
    </div>
  );
}
