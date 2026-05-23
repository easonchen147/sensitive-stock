from __future__ import annotations

from datetime import date
from typing import Any

from ..schemas.research import ScreenerExportRequest, ScreenerFilters, ScreenerRunRequest
from .market_data import AkshareMarketDataService


class ScreenerService:
    def __init__(self, market_data_service: Any | None = None) -> None:
        self.market_data_service = market_data_service or AkshareMarketDataService()

    def list_templates(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "templates": [
                {
                    "id": "momentum",
                    "label": "动量候选",
                    "filters": {"minChangePercent": 0},
                    "sortBy": "score",
                },
                {
                    "id": "low_price_rebound",
                    "label": "低价反弹观察",
                    "filters": {"maxPrice": 20, "minChangePercent": -2},
                    "sortBy": "changePercent",
                },
            ],
            "metadata": {
                "source": "akshare",
                "degraded": False,
                "supportsNaturalLanguage": True,
                "supportsBacktestHandoff": True,
            },
        }

    def run(self, request: ScreenerRunRequest) -> dict[str, Any]:
        interpreted_filters = self._interpret_prompt(request.prompt, request.filters)
        source = "akshare"
        degraded = False
        warnings: list[str] = []

        try:
            quote_payload = self.market_data_service.get_quotes(request.universe)
            quotes = quote_payload.get("items", [])
            source = quote_payload.get("source", source)
        except Exception as error:  # pragma: no cover - exercised through API behavior
            quotes = []
            degraded = True
            warnings.append(f"行情报价源暂不可用：{error}")

        items = [
            self._serialize_candidate(quote, interpreted_filters)
            for quote in quotes
            if self._matches_filters(quote, interpreted_filters)
        ]
        items.sort(key=lambda item: item.get(request.sort_by, 0) or 0, reverse=True)
        items = items[: request.limit]

        return {
            "items": items,
            "summary": {
                "universeSize": len(request.universe),
                "matchCount": len(items),
                "sortBy": request.sort_by,
            },
            "appliedFilters": interpreted_filters.model_dump(by_alias=True, exclude_none=True),
            "interpretedPrompt": request.prompt or "",
            "exportRows": [self._export_row(item) for item in items],
            "backtestHandoff": self._build_backtest_handoff(
                [item["symbol"] for item in items],
                request.backtest_start_date,
                request.backtest_end_date,
            ),
            "metadata": {
                "source": source,
                "degraded": degraded,
                "warnings": warnings,
            },
        }

    def export(self, request: ScreenerExportRequest) -> dict[str, Any]:
        result = self.run(request)
        return {
            "format": request.format,
            "columns": ["symbol", "name", "score", "price", "changePercent", "factorSummary"],
            "rows": result["exportRows"],
            "metadata": result["metadata"],
        }

    def _interpret_prompt(self, prompt: str | None, filters: ScreenerFilters) -> ScreenerFilters:
        merged = filters.model_dump()
        normalized_prompt = (prompt or "").lower()
        if normalized_prompt:
            momentum_tokens = ("momentum", "strong", "breakout", "up")
            if any(token in normalized_prompt for token in momentum_tokens):
                merged["min_change_percent"] = merged["min_change_percent"] or 0
            if "low price" in normalized_prompt or "cheap" in normalized_prompt:
                merged["max_price"] = merged["max_price"] or 20
            if "rebound" in normalized_prompt:
                merged["min_change_percent"] = merged["min_change_percent"] or -2
        return ScreenerFilters.model_validate(merged)

    def _matches_filters(self, quote: dict[str, Any], filters: ScreenerFilters) -> bool:
        price = _to_float(quote.get("price"))
        change_percent = _to_float(quote.get("changePercent"))
        if filters.min_price is not None and price < filters.min_price:
            return False
        if filters.max_price is not None and price > filters.max_price:
            return False
        if filters.min_change_percent is not None and change_percent < filters.min_change_percent:
            return False
        if filters.max_change_percent is not None and change_percent > filters.max_change_percent:
            return False
        return True

    def _serialize_candidate(
        self,
        quote: dict[str, Any],
        filters: ScreenerFilters,
    ) -> dict[str, Any]:
        price = _to_float(quote.get("price"))
        change_percent = _to_float(quote.get("changePercent"))
        score = round(change_percent * 1.8 + min(max(price, 0), 100) * 0.02, 4)
        matched_rules = []
        if filters.min_change_percent is not None:
            matched_rules.append(f"changePercent >= {filters.min_change_percent}")
        if filters.max_price is not None:
            matched_rules.append(f"price <= {filters.max_price}")
        if filters.min_price is not None:
            matched_rules.append(f"price >= {filters.min_price}")
        return {
            "symbol": str(quote.get("symbol", "")),
            "name": quote.get("name") or quote.get("symbol", ""),
            "price": price,
            "changePercent": change_percent,
            "score": score,
            "matchedRules": matched_rules,
            "factorSummary": {
                "momentum": change_percent,
                "liquidity": _to_float(quote.get("amount")) or _to_float(quote.get("volume")),
            },
        }

    def _export_row(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "symbol": item["symbol"],
            "name": item["name"],
            "score": item["score"],
            "price": item["price"],
            "changePercent": item["changePercent"],
            "factorSummary": item["factorSummary"],
        }

    def _build_backtest_handoff(
        self,
        symbols: list[str],
        start_date: date | None,
        end_date: date | None,
    ) -> dict[str, Any]:
        return {
            "endpoint": "/api/v1/backtests/run",
            "payload": {
                "market": {
                    "symbols": symbols[:5],
                    "startDate": str(start_date or date(2025, 1, 1)),
                    "endDate": str(end_date or date(2025, 12, 31)),
                    "adjust": "qfq",
                },
                "strategy": {
                    "mode": "preset",
                    "presetId": "ma_cross",
                    "code": "",
                    "params": {"fast_window": 5, "slow_window": 20},
                },
                "execution": {"mode": "close", "positionSize": 1.0, "lotSize": 100},
                "costs": {"tradingFee": 0.0005, "stampTax": 0.001, "slippage": 0.0},
                "risk": {"stopLoss": 0.0, "takeProfit": 0.0},
                "initialCapital": 100000,
            },
        }


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
