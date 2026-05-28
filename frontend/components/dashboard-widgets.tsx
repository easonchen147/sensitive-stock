"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { getMarketSectors, getMarketNews } from "@/lib/api"
import type { MarketSector, MarketNewsItem } from "@/types/api"
import {
  Search,
  Stethoscope,
  FlaskConical,
  BarChart3,
  Bot,
} from "lucide-react"

export function HotSectors() {
  const [sectors, setSectors] = useState<MarketSector[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMarketSectors("concept", 5)
      .then((r) => {
        setSectors(r.items || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading)
    return <div className="text-sm text-muted-foreground">加载中...</div>

  return (
    <div className="space-y-2">
      {sectors.map((s) => (
        <div
          key={s.code || s.name}
          className="flex items-center justify-between text-sm"
        >
          <span>{s.name}</span>
          <Badge
            variant={
              Number(s.changePercent) >= 0 ? "default" : "destructive"
            }
          >
            {s.changePercent?.toFixed(2)}%
          </Badge>
        </div>
      ))}
    </div>
  )
}

export function LatestNews() {
  const [news, setNews] = useState<MarketNewsItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMarketNews(5)
      .then((r) => {
        setNews(r.items || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading)
    return <div className="text-sm text-muted-foreground">加载中...</div>

  return (
    <div className="space-y-2">
      {news.map((n, i) => (
        <div key={n.id || i} className="text-sm border-b pb-2 last:border-0">
          <div className="font-medium line-clamp-1">{n.title}</div>
          <div className="text-xs text-muted-foreground">{n.publishedAt}</div>
        </div>
      ))}
    </div>
  )
}

const QUICK_LINKS = [
  { href: "/diagnosis", label: "诊股报告", icon: Stethoscope },
  { href: "/backtests", label: "回测验证", icon: FlaskConical },
  { href: "/screener", label: "选股研究", icon: BarChart3 },
  { href: "/qa", label: "AI 问答", icon: Bot },
]

export function QuickActions() {
  const router = useRouter()
  const [symbol, setSymbol] = useState("")

  const handleSearch = () => {
    const trimmed = symbol.trim()
    if (trimmed) {
      router.push(`/stocks/${trimmed}`)
    }
  }

  return (
    <Card>
      <CardHeader>
        <span className="text-xs font-bold uppercase tracking-wider text-primary">
          快速操作
        </span>
        <CardTitle className="font-display">常用入口</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="输入股票代码查看详情（如 000001）"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <Button onClick={handleSearch} disabled={!symbol.trim()}>
            <Search className="size-4" />
          </Button>
        </div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {QUICK_LINKS.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 rounded-lg border border-border p-3 text-sm transition-colors hover:bg-muted/50"
              >
                <Icon className="size-4 text-primary" />
                <span className="font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
