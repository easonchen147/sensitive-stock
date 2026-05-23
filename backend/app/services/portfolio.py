from __future__ import annotations

from typing import Any

from portfolio_optimizer import PortfolioOptimizer

from ..schemas.research import PortfolioOptimizationRequest


class PortfolioOptimizationService:
    def __init__(self, optimizer: PortfolioOptimizer | None = None) -> None:
        self.optimizer = optimizer or PortfolioOptimizer()

    def describe(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "objectives": ["equal_weight", "minimum_variance", "maximum_sharpe", "risk_parity"],
            "metadata": {"source": "akshare", "degraded": False},
        }

    def optimize(self, request: PortfolioOptimizationRequest) -> dict[str, Any]:
        symbols = request.symbols
        start_date = str(request.start_date)
        end_date = str(request.end_date)

        if request.objective == "equal_weight":
            weights = self.optimizer.equal_weight_portfolio(symbols)
        elif request.objective == "minimum_variance":
            weights = self.optimizer.minimum_variance_portfolio(symbols, start_date, end_date)
        elif request.objective == "risk_parity":
            weights = self.optimizer.risk_parity_portfolio(symbols, start_date, end_date)
        else:
            weights = self.optimizer.maximum_sharpe_portfolio(
                symbols,
                start_date,
                end_date,
                risk_free_rate=request.risk_free_rate,
            )

        metrics = self.optimizer.calculate_portfolio_metrics(symbols, weights, start_date, end_date)
        allocations = [
            {"symbol": symbol, "weight": round(float(weights.get(symbol, 0.0)), 6)}
            for symbol in symbols
        ]
        return {
            "objective": request.objective,
            "window": {
                "startDate": start_date,
                "endDate": end_date,
                "riskFreeRate": request.risk_free_rate,
            },
            "allocations": allocations,
            "statistics": _normalize_metrics(metrics),
            "metadata": {
                "source": "akshare",
                "degraded": not bool(metrics),
                "warnings": ["组合统计指标暂不可用"] if not metrics else [],
            },
        }


def _normalize_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for key, value in metrics.items():
        normalized[_normalize_key(str(key))] = _to_float(value)
    return normalized


def _normalize_key(value: str) -> str:
    lower = value.lower()
    if "return" in lower or "收益" in value:
        return "totalReturn" if "total" in lower or "总" in value else "annualReturn"
    if "vol" in lower or "波动" in value:
        return "volatility"
    if "sharpe" in lower or "夏普" in value:
        return "sharpeRatio"
    if "drawdown" in lower or "回撤" in value:
        return "maxDrawdown"
    return lower.replace(" ", "_")


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
