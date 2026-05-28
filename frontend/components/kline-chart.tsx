"use client"
import { useEffect, useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { getKlineData } from "@/lib/api"
import type { KlineDataPoint } from "@/types/api"
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  ReferenceLine,
} from "recharts"

interface KlineChartProps {
  symbol: string
  period?: string
  height?: number
}

type MaKey = "ma5" | "ma10" | "ma20" | "ma60"

const MA_CONFIG: Record<MaKey, { period: number; color: string; label: string }> = {
  ma5: { period: 5, color: "hsl(45, 90%, 55%)", label: "MA5" },
  ma10: { period: 10, color: "hsl(200, 80%, 55%)", label: "MA10" },
  ma20: { period: 20, color: "hsl(280, 70%, 60%)", label: "MA20" },
  ma60: { period: 60, color: "hsl(150, 70%, 45%)", label: "MA60" },
}

function computeMA(data: KlineDataPoint[], period: number): (number | null)[] {
  return data.map((_, i) => {
    if (i < period - 1) return null
    let sum = 0
    for (let j = i - period + 1; j <= i; j++) {
      sum += data[j].close ?? 0
    }
    return sum / period
  })
}

interface TooltipPayloadEntry {
  dataKey: string
  value: number
  color: string
}

function KlineTooltip({ active, payload, label }: { active?: boolean; payload?: TooltipPayloadEntry[]; label?: string }) {
  if (!active || !payload?.length) return null
  const candleData = payload.find(p => p.dataKey === "candleRange")
  const volumeData = payload.find(p => p.dataKey === "volume")
  const raw = candleData?.value
  const ohlc = raw && Array.isArray(raw) ? raw : null

  return (
    <div className="rounded-lg border bg-card p-3 text-xs shadow-md space-y-1.5">
      <div className="font-semibold text-sm">{label}</div>
      {ohlc && (
        <div className="grid grid-cols-2 gap-x-4 gap-y-0.5">
          <span className="text-muted-foreground">开盘</span><span className="font-mono">{Number(ohlc[0]).toFixed(2)}</span>
          <span className="text-muted-foreground">最高</span><span className="font-mono">{Number(ohlc[1]).toFixed(2)}</span>
          <span className="text-muted-foreground">最低</span><span className="font-mono">{Number(ohlc[2]).toFixed(2)}</span>
          <span className="text-muted-foreground">收盘</span><span className="font-mono">{Number(ohlc[3]).toFixed(2)}</span>
        </div>
      )}
      {volumeData && (
        <div className="flex justify-between border-t pt-1">
          <span className="text-muted-foreground">成交量</span>
          <span className="font-mono">{Number(volumeData.value).toLocaleString()}</span>
        </div>
      )}
      {payload.filter(p => p.dataKey.startsWith("ma")).map(p => (
        <div key={p.dataKey} className="flex justify-between">
          <span style={{ color: p.color }}>{p.dataKey.toUpperCase()}</span>
          <span className="font-mono">{Number(p.value).toFixed(2)}</span>
        </div>
      ))}
    </div>
  )
}

export function KlineChart({ symbol, period = "daily", height = 420 }: KlineChartProps) {
  const [data, setData] = useState<KlineDataPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [activePeriod, setActivePeriod] = useState(period)
  const [visibleMA, setVisibleMA] = useState<MaKey[]>(["ma5", "ma10", "ma20"])

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const r = await getKlineData(symbol, activePeriod)
      setData(r.items?.slice(-80) || [])
    } catch {
      setData([])
    } finally {
      setLoading(false)
    }
  }, [symbol, activePeriod])

  useEffect(() => { fetchData() }, [fetchData])

  const periods = [
    { value: "daily", label: "日K" },
    { value: "weekly", label: "周K" },
    { value: "monthly", label: "月K" },
    { value: "60min", label: "60分" },
    { value: "30min", label: "30分" },
  ]

  if (loading) return <div className="flex items-center justify-center text-sm text-muted-foreground p-8">加载K线数据...</div>
  if (!data.length) return <div className="flex items-center justify-center text-sm text-muted-foreground p-8">暂无K线数据</div>

  // Compute MA data
  const maData: Record<MaKey, (number | null)[]> = {} as Record<MaKey, (number | null)[]>
  for (const key of Object.keys(MA_CONFIG) as MaKey[]) {
    maData[key] = computeMA(data, MA_CONFIG[key].period)
  }

  // Price range for Y axis
  let priceMin = Infinity, priceMax = -Infinity
  for (const d of data) {
    if (d.low != null && d.low < priceMin) priceMin = d.low
    if (d.high != null && d.high > priceMax) priceMax = d.high
  }
  // Include MA values in range
  for (const key of visibleMA) {
    for (const v of maData[key]) {
      if (v != null) {
        if (v < priceMin) priceMin = v
        if (v > priceMax) priceMax = v
      }
    }
  }
  const pricePad = (priceMax - priceMin) * 0.08 || 1

  // Volume max for secondary Y axis
  let volMax = 0
  for (const d of data) {
    if (d.volume != null && d.volume > volMax) volMax = d.volume
  }

  // Chart data with MA values
  const chartData = data.map((d, i) => {
    const bullish = (d.close || 0) >= (d.open || 0)
    const row: Record<string, number | string | null | number[]> = {
      date: d.date?.slice(5) || "",
      candleRange: [d.open ?? 0, d.high ?? 0, d.low ?? 0, d.close ?? 0],
      wickHigh: d.high,
      wickLow: d.low,
      volume: d.volume,
      bullish: bullish ? 1 : 0,
      volFill: bullish ? "hsl(var(--chart-1))" : "hsl(var(--destructive))",
    }
    for (const key of Object.keys(MA_CONFIG) as MaKey[]) {
      row[key] = maData[key][i]
    }
    return row
  })

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle className="text-base">{symbol} K线图</CardTitle>
          <div className="flex items-center gap-2">
            <ToggleGroup
              type="multiple"
              variant="outline"
              size="sm"
              value={visibleMA}
              onValueChange={(v) => setVisibleMA((v || []) as MaKey[])}
              className="h-7"
            >
              {(Object.keys(MA_CONFIG) as MaKey[]).map(key => (
                <ToggleGroupItem
                  key={key}
                  value={key}
                  className="h-7 px-2 text-xs"
                  style={visibleMA.includes(key) ? { color: MA_CONFIG[key].color, borderColor: MA_CONFIG[key].color } : undefined}
                >
                  {MA_CONFIG[key].label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>
        </div>
        <div className="flex gap-1 mt-1">
          {periods.map(p => (
            <Button
              key={p.value}
              variant={activePeriod === p.value ? "default" : "ghost"}
              size="sm"
              className="h-6 text-xs px-2"
              onClick={() => setActivePeriod(p.value)}
            >
              {p.label}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              stroke="hsl(var(--muted-foreground))"
              interval="preserveStartEnd"
            />
            <YAxis
              yAxisId="price"
              tick={{ fontSize: 10 }}
              stroke="hsl(var(--muted-foreground))"
              domain={[priceMin - pricePad, priceMax + pricePad]}
              tickFormatter={(v: number) => v.toFixed(2)}
              width={60}
            />
            <YAxis
              yAxisId="volume"
              orientation="right"
              tick={{ fontSize: 9 }}
              stroke="hsl(var(--muted-foreground))"
              domain={[0, volMax * 4]}
              tickFormatter={(v: number) => v >= 1e8 ? `${(v / 1e8).toFixed(0)}亿` : v >= 1e4 ? `${(v / 1e4).toFixed(0)}万` : String(v)}
              width={50}
            />
            <Tooltip content={<KlineTooltip />} />

            {/* MA lines */}
            {(Object.keys(MA_CONFIG) as MaKey[]).map(key => (
              visibleMA.includes(key) && (
                <Line
                  key={key}
                  yAxisId="price"
                  type="monotone"
                  dataKey={key}
                  stroke={MA_CONFIG[key].color}
                  strokeWidth={1.2}
                  dot={false}
                  connectNulls={false}
                  isAnimationActive={false}
                />
              )
            ))}

            {/* Candlestick bodies + wicks as bars: [open, close] */}
            <Bar
              yAxisId="price"
              dataKey="candleRange"
              barSize={Math.max(3, Math.min(10, 600 / data.length))}
              isAnimationActive={false}
              shape={(props: { x?: number; y?: number; width?: number; height?: number; payload?: Record<string, unknown> }) => {
                const { x, y, width, height: h, payload: p } = props
                if (!p || x == null || y == null || width == null || h == null) return null
                const bullish = p.bullish === 1
                const color = bullish ? "hsl(var(--chart-1))" : "hsl(var(--destructive))"
                const fill = bullish ? color : "hsl(var(--background))"
                const wickX = x + width / 2
                const wickHigh = p.wickHigh as number | null
                const wickLow = p.wickLow as number | null
                // Approximate wick top/bottom from candle body
                const wickTop = Math.min(y, y + h)
                const wickBot = Math.max(y, y + h)
                // Extend wick by a few pixels (approximation)
                const wickExt = 3
                return (
                  <g>
                    <line
                      x1={wickX} y1={wickTop - wickExt}
                      x2={wickX} y2={wickBot + wickExt}
                      stroke={color} strokeWidth={1}
                    />
                    <rect
                      x={x} y={y}
                      width={width} height={Math.max(h, 1)}
                      fill={fill}
                      stroke={color}
                      rx={0.5}
                    />
                  </g>
                )
              }}
            >
              {chartData.map((entry, index) => (
                <Cell key={index} />
              ))}
            </Bar>

            {/* Volume bars */}
            <Bar
              yAxisId="volume"
              dataKey="volume"
              fill="hsl(var(--muted))"
              opacity={0.3}
              barSize={Math.max(2, Math.min(8, 500 / data.length))}
              isAnimationActive={false}
            >
              {chartData.map((entry, index) => (
                <Cell key={index} fill={entry.volFill as string} fillOpacity={0.3} />
              ))}
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
