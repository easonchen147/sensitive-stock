from __future__ import annotations

import pandas as pd

from backtesting.engine import Backtester


def _sample_ohlcv() -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "open": [10.0, 11.0, 12.0, 13.0, 14.0],
            "high": [10.5, 11.5, 12.5, 13.5, 14.5],
            "low": [9.5, 10.5, 11.5, 12.5, 13.5],
            "close": [10.0, 11.0, 12.0, 13.0, 14.0],
            "volume": [1000, 1000, 1000, 1000, 1000],
            "amount": [10000, 11000, 12000, 13000, 14000],
            "pre_close": [9.8, 10.0, 11.0, 12.0, 13.0],
        },
        index=index,
    )


def test_backtester_uses_next_open_round_lot_and_sell_stamp_tax() -> None:
    data = _sample_ohlcv()
    signal = pd.Series([0.0, 1.0, 1.0, 0.0, 0.0], index=data.index)

    backtester = Backtester(
        initial_capital=10000.0,
        trading_fee=0.0005,
        stamp_tax=0.001,
        slippage=0.0,
        execution_mode="next_open",
        position_size=0.95,
        lot_size=100,
    )

    result = backtester.run(data, signal)

    assert len(result.trades) == 2
    buy_trade = result.trades.iloc[0]
    sell_trade = result.trades.iloc[1]

    assert pd.Timestamp(buy_trade["date"]) == pd.Timestamp("2025-01-03")
    assert buy_trade["price"] == 12.0
    assert buy_trade["shares"] == 700
    assert pd.Timestamp(sell_trade["date"]) == pd.Timestamp("2025-01-05")
    assert sell_trade["price"] == 14.0
    assert sell_trade["shares"] == 700
    assert sell_trade["tax"] == 9.8
