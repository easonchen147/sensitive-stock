from __future__ import annotations

import pandas as pd

from app.services.market_data import AkshareMarketDataService


class FailingAkshareClient:
    def stock_zh_a_spot_em(self):  # noqa: ANN201
        raise RuntimeError("akshare quotes unavailable")

    def stock_board_concept_name_em(self):  # noqa: ANN201
        raise RuntimeError("akshare sectors unavailable")

    def stock_board_industry_name_em(self):  # noqa: ANN201
        raise RuntimeError("akshare sectors unavailable")


class EmptyAkshareClient:
    def stock_zh_a_spot_em(self):  # noqa: ANN201
        return pd.DataFrame()

    def stock_board_concept_name_em(self):  # noqa: ANN201
        return pd.DataFrame()


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class SequencedSession:
    def __init__(self, responses: list[FakeResponse | Exception]) -> None:
        self.responses = responses

    def get(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201
        if not self.responses:
            raise RuntimeError("no response configured")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _eastmoney_quote_response() -> FakeResponse:
    return FakeResponse(
        {
            "data": {
                "diff": [
                    {
                        "f12": "1",
                        "f14": "Ping An Bank",
                        "f2": 10.5,
                        "f3": 1.2,
                    }
                ]
            }
        }
    )


def _eastmoney_sector_response() -> FakeResponse:
    return FakeResponse(
        {
            "data": {
                "diff": [
                    {
                        "f12": "BK001",
                        "f14": "Computing",
                        "f3": 3.2,
                    }
                ]
            }
        }
    )


def test_market_quote_success_marks_payload_as_not_degraded() -> None:
    service = AkshareMarketDataService(
        akshare_client=EmptyAkshareClient(),
        session=SequencedSession([]),
    )

    payload = service.get_quotes([])

    assert payload["source"] == "akshare"
    assert payload["degraded"] is False
    assert payload["warnings"] == []


def test_market_quote_fallback_marks_payload_as_degraded() -> None:
    service = AkshareMarketDataService(
        akshare_client=FailingAkshareClient(),
        session=SequencedSession([_eastmoney_quote_response()]),
        retry_attempts=1,
    )

    payload = service.get_quotes(["000001"])

    assert payload["source"] == "eastmoney_direct"
    assert payload["degraded"] is True
    assert "主行情报价源暂不可用" in payload["warnings"][0]
    assert payload["items"][0]["symbol"] == "000001"


def test_market_quote_refresh_failure_returns_cached_degraded_payload() -> None:
    service = AkshareMarketDataService(
        akshare_client=FailingAkshareClient(),
        session=SequencedSession([_eastmoney_quote_response(), RuntimeError("eastmoney down")]),
        retry_attempts=1,
    )

    first_payload = service.get_quotes(["000001"])
    cached_payload = service.get_quotes(["000001"])

    assert first_payload["items"][0]["symbol"] == "000001"
    assert cached_payload["degraded"] is True
    assert cached_payload["items"][0]["symbol"] == "000001"
    assert any("已使用缓存行情数据" in warning for warning in cached_payload["warnings"])


def test_market_quote_failure_without_cache_returns_degraded_empty_payload() -> None:
    service = AkshareMarketDataService(
        akshare_client=FailingAkshareClient(),
        session=SequencedSession([RuntimeError("eastmoney down")]),
        retry_attempts=1,
    )

    payload = service.get_quotes(["000001"])

    assert payload["source"] == "unavailable"
    assert payload["degraded"] is True
    assert payload["items"] == []
    assert any("暂未获得可用行情数据" in warning for warning in payload["warnings"])


def test_market_sector_refresh_failure_returns_cached_degraded_payload() -> None:
    service = AkshareMarketDataService(
        akshare_client=FailingAkshareClient(),
        session=SequencedSession([_eastmoney_sector_response(), RuntimeError("eastmoney down")]),
        retry_attempts=1,
    )

    first_payload = service.get_hot_sectors(limit=1, sector_type="concept")
    cached_payload = service.get_hot_sectors(limit=1, sector_type="concept")

    assert first_payload["items"][0]["name"] == "Computing"
    assert cached_payload["degraded"] is True
    assert cached_payload["items"][0]["name"] == "Computing"
    assert any("已使用缓存行情数据" in warning for warning in cached_payload["warnings"])


def test_market_sector_failure_without_cache_returns_degraded_empty_payload() -> None:
    service = AkshareMarketDataService(
        akshare_client=FailingAkshareClient(),
        session=SequencedSession([RuntimeError("eastmoney down")]),
        retry_attempts=1,
    )

    payload = service.get_hot_sectors(limit=1, sector_type="concept")

    assert payload["source"] == "unavailable"
    assert payload["degraded"] is True
    assert payload["sectorType"] == "concept"
    assert payload["items"] == []
    assert any("暂未获得可用行情数据" in warning for warning in payload["warnings"])
