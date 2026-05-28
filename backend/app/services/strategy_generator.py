from __future__ import annotations
import json
from typing import Any
import requests
from .runtime_cache import TTLCache
from .deepseek_prediction import DeepSeekMarketPredictionService

STRATEGY_SYSTEM_PROMPT = """你是 A 股量化策略代码生成助手。
根据用户的中文策略描述，生成符合 akquant 回测引擎规范的 Python 策略代码。

规则：
1. 只生成一个 `generate_signals(data, ctx)` 函数
2. data 包含: open, high, low, close, volume 列（pandas Series）
3. ctx 可用方法：
   - ctx.sma(series, window) - 简单移动平均
   - ctx.ema(series, window) - 指数移动平均
   - ctx.rsi(series, window) - RSI 指标
   - ctx.cross_over(a, b) - a 上穿 b
   - ctx.cross_under(a, b) - a 下穿 b
   - ctx.new_signal() - 创建新信号 Series
   - ctx.params.get("key", default) - 获取参数
4. 返回值必须是 0/1 信号 Series（1=买入持有，0=卖出空仓）
5. 信号要通过 ffill().fillna(0) 处理
6. 只返回 JSON，格式：
{
  "code": "generate_signals 函数代码",
  "params": {"key": default_value},
  "parameterSchema": [{"name": "key", "label": "中文标签", "type": "number", "default": 0, "min": 0, "max": 100, "step": 1, "helpText": "说明"}],
  "explanation": "策略逻辑中文说明",
  "riskNotes": ["风险提示1", "风险提示2"]
}
7. 所有可读文本使用简体中文
8. 代码中不要包含 import 语句
"""

class StrategyGeneratorService:
    def __init__(self, deepseek_service: DeepSeekMarketPredictionService | None = None):
        self.deepseek_service = deepseek_service
        self._cache = TTLCache(300)

    def generate(self, description: str) -> dict[str, Any]:
        """Generate strategy code from natural language description."""
        if not self.deepseek_service or not self.deepseek_service.api_key:
            return {
                "error": "DeepSeek API key not configured",
                "degraded": True,
                "code": "",
                "params": {},
                "parameterSchema": [],
                "explanation": "需要配置 DEEPSEEK_API_KEY 才能使用自然语言策略生成功能。",
                "riskNotes": ["请在 .env 中配置 DEEPSEEK_API_KEY"],
            }

        cache_key = ("strategy_gen", description)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = self._call_deepseek(description)
            result = self._parse_response(response)
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "degraded": True,
                "code": "",
                "params": {},
                "parameterSchema": [],
                "explanation": f"策略生成失败：{e}",
                "riskNotes": ["请检查 DeepSeek API 配置"],
            }

    def _call_deepseek(self, description: str) -> str:
        """Call DeepSeek API to generate strategy."""
        url = f"{self.deepseek_service.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_service.api_key}",
        }
        payload = {
            "model": self.deepseek_service.model,
            "messages": [
                {"role": "system", "content": STRATEGY_SYSTEM_PROMPT},
                {"role": "user", "content": description},
            ],
            "temperature": 0.3,
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

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse DeepSeek response into structured strategy."""
        # Try to extract JSON from the response
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            parsed = json.loads(content)
            # Validate required fields
            code = parsed.get("code", "")
            if "def generate_signals" not in code:
                code = f"def generate_signals(data, ctx):\n{code}"

            return {
                "code": code,
                "params": parsed.get("params", {}),
                "parameterSchema": parsed.get("parameterSchema", []),
                "explanation": parsed.get("explanation", ""),
                "riskNotes": parsed.get("riskNotes", []),
                "degraded": False,
            }
        except json.JSONDecodeError:
            return {
                "code": content,
                "params": {},
                "parameterSchema": [],
                "explanation": "AI 返回的代码已直接使用，请检查格式。",
                "riskNotes": ["AI 生成的策略代码需要人工审核后使用。"],
                "degraded": True,
            }
