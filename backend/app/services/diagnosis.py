from __future__ import annotations

from typing import Any

from ..schemas.research import DiagnosisRequest
from .market_data import AkshareMarketDataService


class DiagnosisService:
    def __init__(self, market_data_service: Any | None = None) -> None:
        self.market_data_service = market_data_service or AkshareMarketDataService()

    def describe(self) -> dict[str, Any]:
        return {
            "status": "migrated",
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
            warnings.append(f"market quote source unavailable: {error}")

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
                    "label": "Intraday momentum",
                    "value": change_percent,
                    "tone": trend_tone,
                },
                {
                    "name": "risk_level",
                    "label": "Risk level",
                    "value": risk_level,
                    "tone": "warning" if risk_level == "elevated" else "neutral",
                },
            ],
            "sections": [
                {
                    "title": "Market context",
                    "tone": trend_tone,
                    "summary": (
                        f"{request.symbol} latest quote is {price:.2f}, "
                        f"with changePercent {change_percent:.2f}%."
                    ),
                },
                {
                    "title": "Technical read",
                    "tone": trend_tone,
                    "summary": (
                        "Momentum is positive." if change_percent >= 0 else "Momentum is weak."
                    ),
                },
                {
                    "title": "Action note",
                    "tone": "neutral",
                    "summary": "Use this report as research context, not as investment advice.",
                },
            ],
            "riskNotes": [
                "Short-term quote data can be noisy.",
                "Validate any diagnosis with backtesting and broader market context.",
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
