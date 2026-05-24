from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import file_env
from backtesting.data import (
    DataProviderError,
    HistoricalDataRequest,
    SmartDataProvider,
    TickflowProvider,
)


@pytest.fixture(autouse=True)
def _clear_backend_file_env_cache() -> None:
    file_env.clear_backend_file_env_cache()
    yield
    file_env.clear_backend_file_env_cache()


def _build_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_values: dict[str, str] | None = None,
) -> SmartDataProvider:
    payload = env_values or {}
    lines = [f"{key}={value}" for key, value in payload.items()]
    (tmp_path / ".env").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    monkeypatch.setattr(file_env, "BACKEND_ROOT", tmp_path)
    file_env.clear_backend_file_env_cache()
    return SmartDataProvider()


def test_smart_data_provider_reports_akshare_tickflow_first_priority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _build_provider(
        tmp_path,
        monkeypatch,
        {
            "TUSHARE_TOKEN": "token",
        },
    )

    assert provider.describe_source_order() == [
        "akshare",
        "tickflow",
        "tushare",
        "sina_direct",
    ]


def test_smart_data_provider_can_prefer_tickflow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _build_provider(
        tmp_path,
        monkeypatch,
        {
            "BACKEND_MARKET_DATA_PREFER_TICKFLOW": "true",
        },
    )

    assert provider.describe_source_order() == [
        "tickflow",
        "akshare",
        "sina_direct",
    ]


def test_smart_data_provider_can_disable_tickflow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _build_provider(
        tmp_path,
        monkeypatch,
        {
            "BACKEND_MARKET_DATA_ENABLE_TICKFLOW": "false",
            "TUSHARE_TOKEN": "token",
        },
    )

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
