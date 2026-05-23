from __future__ import annotations

from typing import Any

from ..schemas.research import DiagnosisRequest
from .market_data import AkshareMarketDataService


class DiagnosisService:
    def __init__(self, market_data_service: Any | None = None) -> None:
        self.market_data_service = market_data_service or AkshareMarketDataService()

    def describe(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "sections": ["market_context", "technical_indicators", "risk_notes", "conclusion"],
            "metadata": {"source": "akshare", "degraded": False},
        }

    def run(self, request: DiagnosisRequest) -> dict[str, Any]:
        unavailable_inputs: list[str] = []
        warnings: list[str] = []
        quote: dict[str, Any] = {"symbol": request.symbol}
        source = "akshare"

        try:
            quote_payload = self.market_data_service.get_quotes([request.symbol])
            source = quote_payload.get("source", source)
            items = quote_payload.get("items", [])
            if items:
                quote = items[0]
            else:
                unavailable_inputs.append("latest_quote")
        except Exception as error:  # pragma: no cover - exercised through API behavior
            unavailable_inputs.append("latest_quote")
            warnings.append(f"行情报价源暂不可用：{error}")

        price = _to_float(quote.get("price"))
        change_percent = _to_float(quote.get("changePercent"))
        trend_tone = "positive" if change_percent >= 0 else "warning"
        risk_level = "elevated" if abs(change_percent) >= 5 else "normal"
        degraded = bool(unavailable_inputs)

        return {
            "symbol": request.symbol,
            "name": quote.get("name") or request.symbol,
            "marketContext": {
                "price": price,
                "changePercent": change_percent,
                "source": source,
            },
            "indicators": [
                {
                    "name": "intraday_momentum",
                    "label": "日内动量",
                    "value": change_percent,
                    "tone": trend_tone,
                },
                {
                    "name": "risk_level",
                    "label": "风险等级",
                    "value": risk_level,
                    "tone": "warning" if risk_level == "elevated" else "neutral",
                },
            ],
            "sections": [
                {
                    "title": "行情背景",
                    "tone": trend_tone,
                    "summary": (
                        f"{request.symbol} 最新报价 {price:.2f}，涨跌幅 {change_percent:.2f}%。"
                    ),
                },
                {
                    "title": "技术观察",
                    "tone": trend_tone,
                    "summary": (
                        "短线动量偏强。" if change_percent >= 0 else "短线动量偏弱。"
                    ),
                },
                {
                    "title": "研究提示",
                    "tone": "neutral",
                    "summary": "本报告只作为研究上下文，不构成投资建议。",
                },
            ],
            "riskNotes": [
                "短期报价数据可能存在噪声。",
                "诊断结论需要结合回测结果和更宽的市场背景验证。",
            ],
            "metadata": {
                "source": source,
                "degraded": degraded,
                "unavailableInputs": unavailable_inputs,
                "warnings": warnings,
            },
        }


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
