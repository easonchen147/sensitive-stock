"use client"
import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { getKlineData } from "@/lib/api"
import type { KlineDataPoint } from "@/types/api"
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts"

interface KlineChartProps {
  symbol: string
  period?: string
  height?: number
}

export function KlineChart({ symbol, period = "daily", height = 400 }: KlineChartProps) {
  const [data, setData] = useState<KlineDataPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [activePeriod, setActivePeriod] = useState(period)

  useEffect(() => {
    setLoading(true)
    getKlineData(symbol, activePeriod).then(r => {
      setData(r.items?.slice(-60) || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [symbol, activePeriod])

  const periods = [
    { value: "daily", label: "日K" },
    { value: "weekly", label: "周K" },
    { value: "monthly", label: "月K" },
    { value: "60min", label: "60分" },
    { value: "30min", label: "30分" },
  ]

  if (loading) return <div className="text-sm text-muted-foreground p-4">加载K线数据...</div>
  if (!data.length) return <div className="text-sm text-muted-foreground p-4">暂无K线数据</div>

  const chartData = data.map(d => ({
    ...d,
    date: d.date?.slice(5) || "",
    candle: [d.open, d.close],
    wick: [d.low, d.high],
    fill: (d.close || 0) >= (d.open || 0) ? "hsl(var(--chart-1))" : "hsl(var(--destructive))",
  }))

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{symbol} K线图</CardTitle>
          <div className="flex gap-1">
            {periods.map(p => (
              <Button
                key={p.value}
                variant={activePeriod === p.value ? "default" : "ghost"}
                size="sm"
                className="h-7 text-xs"
                onClick={() => setActivePeriod(p.value)}
              >
                {p.label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" />
            <YAxis tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" domain={["dataMin", "dataMax"]} />
            <Tooltip
              contentStyle={{
                background: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "0.5rem",
                fontSize: 12,
              }}
              formatter={(value, name) => {
                const num = Number(value)
                if (name === "volume") return [num.toLocaleString(), "成交量"]
                return [num.toFixed(2), name]
              }}
            />
            <Bar dataKey="volume" fill="hsl(var(--muted))" yAxisId={0}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
