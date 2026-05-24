from __future__ import annotations

import pandas as pd

from backtesting.data import (
    DataProviderError,
    HistoricalDataRequest,
    SmartDataProvider,
    TickflowProvider,
)


def test_smart_data_provider_reports_akshare_tickflow_first_priority(monkeypatch) -> None:
    monkeypatch.setenv("TUSHARE_TOKEN", "token")
    monkeypatch.delenv("BACKEND_MARKET_DATA_PREFER_TICKFLOW", raising=False)
    monkeypatch.delenv("BACKEND_MARKET_DATA_ENABLE_TICKFLOW", raising=False)

    provider = SmartDataProvider()

    assert provider.describe_source_order() == [
        "akshare",
        "tickflow",
        "tushare",
        "sina_direct",
    ]


def test_smart_data_provider_can_prefer_tickflow(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_MARKET_DATA_PREFER_TICKFLOW", "true")
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)

    provider = SmartDataProvider()

    assert provider.describe_source_order() == [
        "tickflow",
        "akshare",
        "sina_direct",
    ]


def test_smart_data_provider_can_disable_tickflow(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_MARKET_DATA_ENABLE_TICKFLOW", "false")
    monkeypatch.setenv("TUSHARE_TOKEN", "token")

    provider = SmartDataProvider()

    assert provider.describe_source_order() == [
        "akshare",
        "tushare",
        "sina_direct",
    ]
    assert "TickFlow disabled" in provider.describe_sources()["skippedProviders"][0]


def test_tickflow_provider_normalizes_daily_ohlcv() -> None:
    class FakeKlines:
        def get(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201
            assert args[0] == "000001.SZ"
            assert kwargs["period"] == "1d"
            assert kwargs["adjust"] == "forward"
            return pd.DataFrame(
                {
                    "trade_date": ["2025-01-02", "2025-01-03"],
                    "open": [10.0, 10.5],
                    "high": [10.8, 10.9],
                    "low": [9.8, 10.2],
                    "close": [10.4, 10.7],
                    "volume": [1000, 1200],
                    "amount": [10400, 12840],
                }
            )

    class FakeClient:
        klines = FakeKlines()

    provider = TickflowProvider(client_factory=lambda: FakeClient())
    frame = provider.get_ohlcv(
        HistoricalDataRequest(
            symbol="000001",
            start_date="2025-01-02",
            end_date="2025-01-03",
            adjust="qfq",
        )
    )

    assert list(frame.columns) == [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "pre_close",
    ]
    assert frame.iloc[0]["pre_close"] == 10.0
    assert frame.iloc[1]["pre_close"] == 10.4


def test_smart_data_provider_records_selected_source_and_errors() -> None:
    class FailingProvider:
        source_name = "broken"

        def get_ohlcv(self, request):  # noqa: ANN001
            raise DataProviderError("boom")

    class SuccessProvider:
        source_name = "success"

        def get_ohlcv(self, request):  # noqa: ANN001
            return pd.DataFrame(
                {
                    "open": [1.0],
                    "high": [1.0],
                    "low": [1.0],
                    "close": [1.0],
                    "volume": [1.0],
                    "amount": [1.0],
                    "pre_close": [1.0],
                },
                index=pd.to_datetime(["2025-01-02"]),
            )

    provider = SmartDataProvider()
    provider.providers = [FailingProvider(), SuccessProvider()]

    frame = provider.get_ohlcv(
        HistoricalDataRequest(
            symbol="000001",
            start_date="2025-01-02",
            end_date="2025-01-02",
        )
    )

    assert not frame.empty
    source_details = provider.describe_sources()
    assert source_details["lastSuccessSource"] == "success"
    assert source_details["providerErrors"] == ["broken: boom"]
