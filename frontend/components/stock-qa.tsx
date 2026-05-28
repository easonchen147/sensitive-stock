"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { askStockQuestion } from "@/lib/api"
import { Send, Bot, User } from "lucide-react"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
  sources?: string[]
  dataReferences?: Array<{ symbol: string; name: string; type: string }>
}

export function StockQAChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [symbols, setSymbols] = useState("")
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      const viewport = scrollRef.current.querySelector(
        "[data-slot='scroll-area-viewport']",
      )
      if (viewport) {
        viewport.scrollTop = viewport.scrollHeight
      }
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const question = input.trim()
    const symbolList = symbols
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)

    setMessages((prev) => [...prev, { role: "user", content: question }])
    setInput("")
    setLoading(true)

    try {
      const result = await askStockQuestion(question, symbolList)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          dataReferences: result.dataReferences,
        },
      ])
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "请求失败"
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `抱歉，发生了错误：${message}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-3 flex gap-2">
        <Input
          placeholder="股票代码（可选，逗号分隔，如 000001,600000）"
          value={symbols}
          onChange={(e) => setSymbols(e.target.value)}
          className="max-w-md"
        />
      </div>

      <Card className="flex-1 flex flex-col min-h-0">
        <div ref={scrollRef} className="flex-1 min-h-0">
          <ScrollArea className="h-full p-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-12">
                <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>输入你的股票问题开始对话</p>
                <p className="text-xs mt-1">
                  例如：平安银行最近的走势怎么样？
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg p-3 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 flex gap-1 flex-wrap">
                      {msg.sources.map((s) => (
                        <Badge key={s} variant="outline" className="text-xs">
                          {s}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary animate-pulse" />
                </div>
                <div className="bg-muted rounded-lg p-3 text-sm">思考中...</div>
              </div>
            )}
          </div>
        </ScrollArea>
        </div>
        <div className="p-4 border-t flex gap-2">
          <Input
            placeholder="输入你的股票问题..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={loading || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </Card>
    </div>
  )
}
