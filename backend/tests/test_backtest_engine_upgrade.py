from __future__ import annotations

import pandas as pd
import pytest

from app.schemas.backtests import BacktestRunRequest
from app.services.backtests_akquant import AKQuantBacktestService


class StubMarketDataProvider:
    def get_ohlcv(self, request):  # noqa: ANN001
        if request.symbol == "159919":
            return _benchmark_ohlcv()
        return _sample_ohlcv()

    def describe_sources(self) -> dict[str, object]:
        return {
            "primarySource": "stub_market",
            "fallbackSources": [],
        }


def _sample_ohlcv() -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=6, freq="D")
    return pd.DataFrame(
        {
            "open": [10.0, 11.0, 12.0, 13.0, 14.0, 14.2],
            "high": [10.5, 11.5, 12.5, 13.5, 14.2, 14.6],
            "low": [9.5, 10.5, 11.5, 12.5, 13.5, 14.0],
            "close": [10.0, 11.0, 12.0, 11.0, 10.0, 14.4],
            "volume": [1000, 1000, 1000, 1000, 1000, 1000],
            "amount": [10000, 11000, 12000, 11000, 10000, 14400],
            "pre_close": [9.8, 10.0, 11.0, 12.0, 11.0, 10.0],
        },
        index=index,
    )


def _benchmark_ohlcv() -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=6, freq="D")
    return pd.DataFrame(
        {
            "open": [10.0, 10.4, 10.8, 11.0, 11.4, 11.7],
            "high": [10.1, 10.5, 10.9, 11.2, 11.6, 11.9],
            "low": [9.9, 10.3, 10.7, 10.9, 11.3, 11.5],
            "close": [10.0, 10.5, 11.0, 11.5, 12.0, 12.2],
            "volume": [1000, 1000, 1000, 1000, 1000, 1000],
            "amount": [10000, 10500, 11000, 11500, 12000, 12200],
            "pre_close": [9.9, 10.0, 10.5, 11.0, 11.5, 12.0],
        },
        index=index,
    )


def _build_request(strategy_code: str, *, stop_loss: float = 0.0, take_profit: float = 0.0):
    return BacktestRunRequest.model_validate(
        {
            "market": {
                "symbols": ["000001"],
                "startDate": "2025-01-01",
                "endDate": "2025-01-06",
                "adjust": "qfq",
                "benchmarkSymbol": "159919",
            },
            "strategy": {
                "mode": "custom",
                "code": strategy_code,
                "params": {},
            },
            "execution": {
                "mode": "next_open",
                "positionSize": 0.9,
                "lotSize": 100,
            },
            "costs": {
                "tradingFee": 0.0005,
                "stampTax": 0.001,
                "slippage": 0.0,
            },
            "risk": {
                "stopLoss": stop_loss,
                "takeProfit": take_profit,
            },
            "initialCapital": 10000,
        }
    )


def test_akquant_service_uses_next_open_round_lot_and_sell_stamp_tax() -> None:
    service = AKQuantBacktestService(market_data_provider_factory=StubMarketDataProvider)
    request = _build_request(
        (
            "def generate_signals(data, ctx):\n"
            "    signal = ctx.new_signal()\n"
            "    signal[data['close'] >= 12] = 1\n"
            "    signal[data['close'] < 12] = 0\n"
            "    return signal.ffill().fillna(0)\n"
        )
    )

    payload = service.run_batch(request)

    assert payload["failures"] == []
    result = payload["results"][0]
    assert result["settings"]["engine"] == "akquant"
    assert result["settings"]["fillPolicy"] == {
        "priceBasis": "open",
        "barOffset": 1,
        "temporal": "same_cycle",
    }
    assert result["trades"][0]["date"] == "2025-01-04"
    assert result["trades"][0]["shares"] == 700
    assert result["trades"][1]["date"] == "2025-01-06"
    assert result["trades"][1]["shares"] == 700
    assert result["trades"][1]["tax"] == pytest.approx(9.94)
    assert result["comparison"]["benchmark_total_return"] is not None
    assert result["tradeStats"]["endingEquity"] > 10000


def test_akquant_service_stop_take_profit_exit_is_reflected_in_trade_reason() -> None:
    service = AKQuantBacktestService(market_data_provider_factory=StubMarketDataProvider)
    request = _build_request(
        (
            "def generate_signals(data, ctx):\n"
            "    signal = ctx.new_signal()\n"
            "    signal[data['close'] >= 12] = 1\n"
            "    return signal.ffill().fillna(0)\n"
        ),
        stop_loss=0.05,
        take_profit=0.1,
    )

    payload = service.run_batch(request)

    assert payload["failures"] == []
    result = payload["results"][0]
    assert any(item["reason"] == "take_profit" for item in result["trades"])
    assert any(item["label"] == "风险控制" for item in result["assumptions"])
