"use client"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { generateStrategy } from "@/lib/api"
import { Wand2, Play, AlertTriangle } from "lucide-react"
import type { StrategyGenerateResponse } from "@/types/api"

interface NLStrategyEditorProps {
  onApply?: (code: string, params: Record<string, unknown>) => void
}

export function NLStrategyEditor({ onApply }: NLStrategyEditorProps) {
  const [description, setDescription] = useState("")
  const [result, setResult] = useState<StrategyGenerateResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!description.trim() || loading) return
    setLoading(true)
    setError(null)
    try {
      const r = await generateStrategy(description.trim())
      setResult(r)
      if (r.error) setError(r.error)
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "生成策略失败"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Wand2 className="w-4 h-4" />
            自然语言策略生成
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Textarea
            placeholder="用中文描述你的交易策略，例如：当5日均线上穿20日均线时买入，下穿时卖出..."
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={3}
          />
          <Button onClick={handleGenerate} disabled={loading || !description.trim()}>
            <Wand2 className="w-4 h-4 mr-2" />
            {loading ? "生成中..." : "生成策略"}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive p-3 bg-destructive/10 rounded-lg">
          <AlertTriangle className="w-4 h-4" />
          {error}
        </div>
      )}

      {result && !error && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">生成结果</CardTitle>
              {result.degraded && <Badge variant="outline">降级模式</Badge>}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {result.explanation && (
              <div className="text-sm text-muted-foreground">{result.explanation}</div>
            )}
            <div className="bg-muted rounded-lg p-3 font-mono text-xs overflow-x-auto">
              <pre className="whitespace-pre-wrap">{result.code}</pre>
            </div>
            {result.riskNotes?.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs font-medium text-muted-foreground">风险提示</div>
                {result.riskNotes.map((note, i) => (
                  <div key={i} className="text-xs text-destructive flex items-start gap-1">
                    <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
                    {note}
                  </div>
                ))}
              </div>
            )}
            {onApply && (
              <Button onClick={() => onApply(result.code, result.params)}>
                <Play className="w-4 h-4 mr-2" />
                应用到回测
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
