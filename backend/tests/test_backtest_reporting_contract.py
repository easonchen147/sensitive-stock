from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

from app.services.backtests import serialize_symbol_result
from app.services.backtests_akquant import AKQuantBacktestService


def test_strategy_presets_expose_summary_and_parameter_help_metadata() -> None:
    payload = AKQuantBacktestService().list_presets()

    ma_cross = next(item for item in payload["items"] if item["id"] == "ma_cross")

    assert ma_cross["summary"]
    assert ma_cross["useCase"]
    assert ma_cross["riskNotes"]
    assert ma_cross["parameterSchema"][0]["helpText"]
    assert ma_cross["parameterSchema"][0]["group"] == "trend"
    assert ma_cross["executionMetadata"]["engine"] == "akquant"
    assert ma_cross["executionMetadata"]["fillPolicies"][0]["priceBasis"] == "close"

    event_momentum = next(
        item for item in payload["items"] if item["id"] == "event_theme_momentum"
    )
    assert event_momentum["summary"]
    assert "预测" in event_momentum["useCase"]
    assert event_momentum["parameterSchema"][0]["group"] == "event"
    assert event_momentum["executionMetadata"]["engine"] == "akquant"


def test_serialize_symbol_result_adds_assumptions_insights_and_derived_trade_stats() -> None:
    index = pd.date_range("2025-01-02", periods=4, freq="D", tz="Asia/Shanghai")
    equity_curve = pd.Series([100000.0, 104000.0, 109000.0, 112000.0], index=index, dtype=float)
    cash_curve = pd.Series([100000.0, 20000.0, 18000.0, 112000.0], index=index, dtype=float)
    metrics_df = pd.DataFrame(
        {
            "value": [
                12.0,
                24.0,
                18.0,
                1.35,
                8.0,
                50.0,
            ]
        },
        index=[
            "total_return_pct",
            "annualized_return",
            "volatility",
            "sharpe_ratio",
            "max_drawdown_pct",
            "win_rate",
        ],
    )
    orders_df = pd.DataFrame(
        [
            {
                "status": "filled",
                "updated_at": pd.Timestamp("2025-01-03", tz="Asia/Shanghai"),
                "side": "buy",
                "avg_price": 10.0,
                "filled_quantity": 8000,
                "quantity": 8000,
                "commission": 40.0,
                "tag": "signal_change",
            },
            {
                "status": "filled",
                "updated_at": pd.Timestamp("2025-01-07", tz="Asia/Shanghai"),
                "side": "sell",
                "avg_price": 14.0,
                "filled_quantity": 8000,
                "quantity": 8000,
                "commission": 168.0,
                "tag": "signal_change",
            },
        ]
    )
    trades_df = pd.DataFrame(
        [
            {
                "duration": pd.Timedelta(days=4),
                "return_pct": 12.0,
                "net_pnl": 12000.0,
            }
        ]
    )
    result = SimpleNamespace(
        equity_curve_daily=equity_curve,
        cash_curve_daily=cash_curve,
        metrics_df=metrics_df,
        orders_df=orders_df,
        trades_df=trades_df,
    )

    benchmark = pd.DataFrame({"close": [100.0, 101.0, 103.0, 106.0]}, index=index)
    settings = {
        "symbol": "000001",
        "initialCapital": 100000.0,
        "benchmarkSymbol": "159919",
        "adjust": "qfq",
        "strategyMode": "preset",
        "strategyPreset": "ma_cross",
        "strategyLabel": "双均线策略",
        "executionMode": "next_open",
        "positionSize": 0.8,
        "lotSize": 100,
        "volumeLimitPct": 0.2,
        "tradingFee": 0.0005,
        "stampTax": 0.001,
        "slippage": 0.0003,
        "minCommission": 5.0,
        "transferFeeRate": 0.00002,
        "stopLoss": 0.06,
        "takeProfit": 0.18,
        "maxDrawdown": 0.12,
        "maxDailyLoss": 1000.0,
        "maxPositionSize": 5000.0,
        "reduceOnlyAfterRisk": True,
        "riskCooldownBars": 3,
        "engine": "akquant",
        "engineVersion": "0.2.37",
        "strategyRiskId": "signal_replay",
        "fillPolicy": {
            "priceBasis": "open",
            "barOffset": 1,
            "temporal": "same_cycle",
        },
        "primarySource": "akshare",
        "fallbackSources": ["tickflow", "tushare", "sina_direct"],
        "sourceOrder": ["akshare", "tickflow", "tushare", "sina_direct"],
        "lastSuccessSource": "akshare",
        "providerErrors": [],
        "skippedProviders": [],
        "dataRows": 4,
        "dataStartDate": "2025-01-02",
        "dataEndDate": "2025-01-05",
    }

    payload = serialize_symbol_result(
        "000001",
        result,
        settings=settings,
        benchmark=benchmark,
        warnings=["基准数据使用 AkShare 主源。"],
        engine_events={
            "totalEvents": 2,
            "warningCount": 1,
            "errorCount": 0,
            "byType": {"progress": 1, "finished": 1},
            "recentTypes": ["progress", "finished"],
            "recentEvents": [],
        },
    )

    assert payload["tradeStats"]["endingEquity"] == 112000.0
    assert payload["tradeStats"]["netProfit"] == 12000.0
    assert payload["tradeStats"]["exposureRate"] == pytest.approx(0.5)
    assert any(
        item["label"] == "执行模式" and item["value"] == "次日开盘成交"
        for item in payload["assumptions"]
    )
    assert any(
        item["label"] == "回测内核" and "akquant" in item["value"]
        for item in payload["assumptions"]
    )
    assert any(
        item["title"] == "相对基准" and item["tone"] == "positive"
        for item in payload["insights"]
    )
    assert payload["trades"][1]["tax"] == pytest.approx(112.0)
    assert payload["dataQuality"]["selectedSource"] == "akshare"
    assert payload["dataQuality"]["sourceOrder"] == [
        "akshare",
        "tickflow",
        "tushare",
        "sina_direct",
    ]
    assert payload["executionQuality"]["volumeLimitPct"] == 0.2
    assert payload["executionQuality"]["filledOrderCount"] == 2
    assert payload["riskDiagnostics"]["maxDrawdownLimit"] == 0.12
    assert payload["riskDiagnostics"]["riskCooldownBars"] == 3
    assert payload["engineEvents"]["warningCount"] == 1
