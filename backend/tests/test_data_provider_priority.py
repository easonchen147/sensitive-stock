from __future__ import annotations

from backtesting.data import SmartDataProvider


def test_smart_data_provider_reports_akshare_first_priority(monkeypatch) -> None:
    monkeypatch.setenv("TUSHARE_TOKEN", "token")

    provider = SmartDataProvider()

    assert provider.describe_source_order() == [
        "akshare",
        "tushare",
        "sina_direct",
    ]
