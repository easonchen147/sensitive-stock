"use client"
import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { getStockDetail } from "@/lib/api"
import type { StockDetail } from "@/types/api"

interface StockDetailPanelProps {
  symbol: string
}

export function StockDetailPanel({ symbol }: StockDetailPanelProps) {
  const [detail, setDetail] = useState<StockDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getStockDetail(symbol).then(d => {
      setDetail(d)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [symbol])

  if (loading) return <div className="text-sm text-muted-foreground">加载中...</div>
  if (!detail || detail.error) return <div className="text-sm text-destructive">无法获取股票信息</div>

  const isPositive = (detail.changePercent || 0) >= 0

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">{detail.name}</CardTitle>
            <div className="text-sm text-muted-foreground">{detail.symbol} · {detail.industry}</div>
          </div>
          <Badge variant={isPositive ? "default" : "destructive"}>
            {isPositive ? "+" : ""}{detail.changePercent?.toFixed(2)}%
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold mb-3">{detail.price?.toFixed(2)}</div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">今开</span><span>{detail.open?.toFixed(2)}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">昨收</span><span>{detail.preClose?.toFixed(2)}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">最高</span><span>{detail.high?.toFixed(2)}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">最低</span><span>{detail.low?.toFixed(2)}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">PE</span><span>{detail.pe?.toFixed(2) || "-"}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">PB</span><span>{detail.pb?.toFixed(2) || "-"}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">换手率</span><span>{detail.turnoverRate?.toFixed(2)}%</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">量比</span><span>{detail.volumeRatio?.toFixed(2) || "-"}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">市值</span><span>{detail.marketCap ? (detail.marketCap / 1e8).toFixed(0) + "亿" : "-"}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">行业</span><span className="truncate">{detail.industry || "-"}</span></div>
        </div>
      </CardContent>
    </Card>
  )
}
