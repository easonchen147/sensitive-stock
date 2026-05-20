from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

from app.services.backtests import serialize_symbol_result
from backtesting.presets import serialize_strategy_presets


def test_strategy_presets_expose_summary_and_parameter_help_metadata() -> None:
    payload = serialize_strategy_presets()

    ma_cross = next(item for item in payload["items"] if item["id"] == "ma_cross")

    assert ma_cross["summary"]
    assert ma_cross["useCase"]
    assert ma_cross["riskNotes"]
    assert ma_cross["parameterSchema"][0]["helpText"]
    assert ma_cross["parameterSchema"][0]["group"] == "trend"


def test_serialize_symbol_result_adds_assumptions_insights_and_derived_trade_stats() -> None:
    index = pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07"])
    performance = pd.DataFrame(
        {
            "strategy_equity": [100000.0, 104000.0, 109000.0, 112000.0],
            "bench_equity": [100000.0, 101000.0, 103000.0, 106000.0],
            "drawdown": [0.0, -0.01, -0.02, -0.015],
            "position": [0.0, 0.8, 0.8, 0.0],
            "cash": [100000.0, 20000.0, 18000.0, 112000.0],
        },
        index=index,
    )
    trades = pd.DataFrame(
        [
            {
                "date": pd.Timestamp("2025-01-03"),
                "action": "Buy",
                "reason": "signal_change",
                "price": 10.0,
                "shares": 8000,
                "notional": 80000.0,
                "fee": 40.0,
                "tax": 0.0,
            },
            {
                "date": pd.Timestamp("2025-01-07"),
                "action": "Sell",
                "reason": "signal_change",
                "price": 14.0,
                "shares": 8000,
                "notional": 112000.0,
                "fee": 56.0,
                "tax": 112.0,
            },
        ]
    )
    monthly_returns = pd.Series(
        [0.12],
        index=pd.to_datetime(["2025-01-31"]),
        dtype=float,
    )
    result = SimpleNamespace(
        settings={
            "symbol": "000001",
            "benchmarkSymbol": "159919",
            "adjust": "qfq",
            "strategyMode": "preset",
            "strategyPreset": "ma_cross",
            "strategyLabel": "双均线策略",
            "executionMode": "next_open",
            "positionSize": 0.8,
            "lotSize": 100,
            "tradingFee": 0.0005,
            "stampTax": 0.001,
            "slippage": 0.0003,
            "stopLoss": 0.06,
            "takeProfit": 0.18,
            "primarySource": "akshare",
            "fallbackSources": ["tushare", "sina_direct"],
        },
        metrics={
            "strategy_total_return": 0.12,
            "annualized_return": 0.24,
            "volatility": 0.18,
            "sharpe": 1.35,
            "max_drawdown": -0.08,
            "win_rate": 0.5,
            "trading_days": 4.0,
        },
        comparison={
            "benchmark_total_return": 0.06,
            "excess_return": 0.06,
            "information_ratio": 0.8,
            "tracking_error": 0.12,
        },
        performance=performance,
        trade_stats={
            "tradeCount": 2,
            "winRate": 1.0,
            "averageHoldingDays": 4.0,
            "averageTradeReturn": 0.12,
            "totalCosts": 208.0,
            "turnover": 1.92,
        },
        trades=trades,
        warnings=["基准数据使用 AkShare 主源。"],
        monthly_returns=monthly_returns,
    )

    payload = serialize_symbol_result("000001", result)

    assert payload["tradeStats"]["endingEquity"] == 112000.0
    assert payload["tradeStats"]["netProfit"] == 12000.0
    assert payload["tradeStats"]["exposureRate"] == pytest.approx(0.5)
    assert any(
        item["label"] == "执行模式" and item["value"] == "next_open"
        for item in payload["assumptions"]
    )
    assert any(
        item["title"] == "相对基准" and item["tone"] == "positive"
        for item in payload["insights"]
    )
