from __future__ import annotations

import pandas as pd

from factor_analysis import FactorAnalyzer
from portfolio_optimizer import PortfolioOptimizer


def _sample_history() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=30, freq="D")
    close = pd.Series(range(10, 40), index=dates, dtype=float)
    return pd.DataFrame(
        {
            "open": close - 0.5,
            "high": close + 0.5,
            "low": close - 1.0,
            "close": close,
            "volume": 1000.0,
            "amount": 10000.0,
            "pre_close": close.shift(1).fillna(close.iloc[0]),
        },
        index=dates,
    )


class StubProvider:
    def __init__(self) -> None:
        self.requests = []

    def get_ohlcv(self, request):  # noqa: ANN001
        self.requests.append(request)
        return _sample_history()


def test_factor_analyzer_uses_unified_ohlcv_contract() -> None:
    provider = StubProvider()
    analyzer = FactorAnalyzer()
    analyzer.data_provider = provider

    factors = analyzer.calculate_factors("000001", "2025-01-01", "2025-01-30")

    assert not factors.empty
    assert provider.requests[0].symbol == "000001"
    assert provider.requests[0].start_date == "2025-01-01"
    assert "momentum_5" in factors.columns


def test_portfolio_optimizer_uses_unified_ohlcv_contract() -> None:
    provider = StubProvider()
    optimizer = PortfolioOptimizer()
    optimizer.data_provider = provider

    returns = optimizer.calculate_returns(["000001", "000002"], "2025-01-01", "2025-01-30")

    assert not returns.empty
    assert len(provider.requests) == 2
    assert list(returns.columns) == ["000001", "000002"]
