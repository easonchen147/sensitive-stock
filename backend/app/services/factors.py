from __future__ import annotations

from typing import Any

from factor_analysis import FactorAnalyzer

from ..schemas.research import FactorAnalysisRequest


class FactorAnalysisService:
    def __init__(self, analyzer: FactorAnalyzer | None = None) -> None:
        self.analyzer = analyzer or FactorAnalyzer()

    def describe(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "supportedFactors": [
                "momentum_5",
                "momentum_10",
                "momentum_20",
                "volatility_10",
                "volatility_20",
                "volume_ratio_5",
                "price_position_20",
            ],
            "metadata": {"source": "akshare", "degraded": False},
        }

    def analyze(self, request: FactorAnalysisRequest) -> dict[str, Any]:
        factors = self.analyzer.calculate_factors(
            request.symbol,
            str(request.start_date),
            str(request.end_date),
        )
        ic_values = self.analyzer.analyze_factor_performance(
            request.symbol,
            str(request.start_date),
            str(request.end_date),
            forward_days=request.forward_days,
        )

        selected_factor_names = request.factors or list(factors.columns)
        selected_factor_names = [name for name in selected_factor_names if name in factors.columns]
        latest_row = factors[selected_factor_names].tail(1).to_dict("records")
        latest_factors = latest_row[0] if latest_row else {}
        ranked_factors = sorted(
            (
                {"name": name, "ic": _to_float(value), "absIc": abs(_to_float(value))}
                for name, value in ic_values.items()
                if not selected_factor_names or name in selected_factor_names
            ),
            key=lambda item: item["absIc"],
            reverse=True,
        )

        degraded = factors.empty
        return {
            "symbol": request.symbol,
            "window": {
                "startDate": str(request.start_date),
                "endDate": str(request.end_date),
                "observations": int(len(factors)),
                "forwardDays": request.forward_days,
            },
            "latestFactors": {key: _to_float(value) for key, value in latest_factors.items()},
            "rankedFactors": ranked_factors[: request.top_n],
            "summary": {
                "factorCount": len(selected_factor_names),
                "topFactor": ranked_factors[0]["name"] if ranked_factors else None,
            },
            "metadata": {
                "source": "akshare",
                "degraded": degraded,
                "warnings": ["no factor observations available"] if degraded else [],
            },
        }


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
