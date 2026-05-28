from __future__ import annotations
from typing import Any
from .deepseek_prediction import DeepSeekMarketPredictionService
from .stock_detail import StockDetailService
from .runtime_cache import TTLCache

QA_SYSTEM_PROMPT = """你是 A 股市场研究助手，基于用户提供的股票数据回答问题。
回答规则：
1. 只基于提供的数据进行分析，不编造数据
2. 所有回答使用简体中文
3. 给出客观分析，不给出买卖建议
4. 如果数据不足，明确说明
5. 回答格式清晰，使用要点列表
6. 结尾提醒："以上分析仅供参考，不构成投资建议。"
"""

class StockQAService:
    def __init__(
        self,
        deepseek_service: DeepSeekMarketPredictionService | None = None,
        stock_detail_service: StockDetailService | None = None,
    ):
        self.deepseek_service = deepseek_service
        self.stock_detail_service = stock_detail_service or StockDetailService()
        self._cache = TTLCache(300)

    def answer(self, question: str, symbols: list[str] | None = None) -> dict[str, Any]:
        """Answer a natural language question about stocks."""
        if not self.deepseek_service or not self.deepseek_service.api_key:
            return {
                "answer": "需要配置 DEEPSEEK_API_KEY 才能使用 AI 问答功能。",
                "sources": [],
                "dataReferences": [],
                "degraded": True,
                "error": "DeepSeek API key not configured",
            }

        cache_key = ("qa", question, tuple(symbols or []))
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # Gather data context for the symbols
            context_parts = []
            data_refs = []

            if symbols:
                for sym in symbols[:5]:  # Limit to 5 symbols
                    detail = self.stock_detail_service.get_stock_detail(sym)
                    if not detail.get("error"):
                        context_parts.append(
                            f"【{detail.get('name', sym)}（{sym}）】\n"
                            f"  行业：{detail.get('industry', '未知')}\n"
                            f"  最新价：{detail.get('price', '未知')}\n"
                            f"  涨跌幅：{detail.get('changePercent', '未知')}%\n"
                            f"  市盈率(PE)：{detail.get('pe', '未知')}\n"
                            f"  市净率(PB)：{detail.get('pb', '未知')}\n"
                            f"  成交量：{detail.get('volume', '未知')}\n"
                            f"  换手率：{detail.get('turnoverRate', '未知')}%"
                        )
                        data_refs.append({"symbol": sym, "name": detail.get("name", sym), "type": "stock_detail"})

                    # Get recent K-line for technical context
                    kline = self.stock_detail_service.get_kline_data(sym, "daily")
                    items = kline.get("items", [])
                    if items:
                        last5 = items[-5:]
                        closes = [it.get("close", 0) for it in last5 if it.get("close")]
                        if closes:
                            context_parts.append(f"  近5日收盘价：{closes}")

            context = "\n".join(context_parts) if context_parts else "未指定具体股票，请基于市场常识回答。"

            # Call DeepSeek
            user_message = f"相关股票数据：\n{context}\n\n用户问题：{question}"

            response = self._call_deepseek(user_message)

            result = {
                "answer": response,
                "sources": [ref["symbol"] for ref in data_refs],
                "dataReferences": data_refs,
                "degraded": False,
            }
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            return {
                "answer": f"回答生成失败：{e}",
                "sources": symbols or [],
                "dataReferences": [],
                "degraded": True,
                "error": str(e),
            }

    def _call_deepseek(self, user_message: str) -> str:
        """Call DeepSeek API."""
        url = f"{self.deepseek_service.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_service.api_key}",
        }
        payload = {
            "model": self.deepseek_service.model,
            "messages": [
                {"role": "system", "content": QA_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.5,
            "max_tokens": 2000,
        }

        if self.deepseek_service.thinking_type == "enabled":
            payload["thinking"] = {"type": "enabled", "reasoning_effort": self.deepseek_service.reasoning_effort}

        response = self.deepseek_service.session.post(
            url, json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        content = ""
        thinking = data.get("thinking", {})
        if isinstance(thinking, dict):
            content = thinking.get("content", "")
        if not content:
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
        return content
