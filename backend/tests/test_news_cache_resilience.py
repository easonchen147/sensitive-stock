from __future__ import annotations

import json

from app.services.news_intelligence import Jin10NewsService, MarketNewsIntelligenceService


class FakeResponse:
    def __init__(self, payload: dict | None = None, text: str = "", status_code: int = 200) -> None:
        self._payload = payload
        self.text = text
        self.status_code = status_code

    def json(self) -> dict:
        if self._payload is None:
            raise ValueError("No JSON payload configured")
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class ToggleSession:
    def __init__(self, flash_items: list[dict]) -> None:
        self.flash_items = flash_items
        self.fail_flash = False
        self.fail_public = False

    def get(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        timeout: int | None = None,
    ):  # noqa: ANN001
        if "get_flash_list" in url:
            if self.fail_flash:
                raise RuntimeError("flash api unavailable")
            return FakeResponse({"status": 200, "message": "OK", "data": self.flash_items})

        if "flash_newest.js" in url:
            if self.fail_public:
                raise RuntimeError("public feed unavailable")
            payload_text = json.dumps(self.flash_items, ensure_ascii=False)
            return FakeResponse(text=f"var newest = {payload_text};")

        raise AssertionError(f"Unexpected url: {url}")


class EmptyMarketDataService:
    def list_sector_catalog(self) -> list[dict[str, str]]:
        return []


def _flash_item(item_id: int) -> dict:
    return {
        "id": f"20260331{item_id:08d}",
        "time": f"2026-03-31 10:{item_id % 60:02d}:00",
        "type": 0,
        "data": {
            "title": f"news {item_id}",
            "content": f"computing topic {item_id}",
            "source": "jin10",
            "source_link": "",
            "pic": "",
        },
        "important": 0,
        "tags": ["computing"],
        "channel": [1, 2, 3],
        "remark": [],
    }


def test_jin10_news_service_returns_cached_payload_when_all_sources_fail() -> None:
    session = ToggleSession([_flash_item(index) for index in range(1, 4)])
    service = Jin10NewsService(session=session, cache_ttl_seconds=300)

    first_payload = service.get_latest(limit=3)
    session.fail_flash = True
    session.fail_public = True
    cached_payload = service.get_latest(limit=3)

    assert first_payload["source"] == "jin10_flash_api"
    assert cached_payload["degraded"] is True
    assert cached_payload["items"][0]["id"] == first_payload["items"][0]["id"]
    assert any("已使用缓存资讯" in warning for warning in cached_payload["warnings"])


def test_news_intelligence_preserves_cached_degraded_metadata() -> None:
    session = ToggleSession([_flash_item(index) for index in range(1, 4)])
    news_service = Jin10NewsService(session=session, cache_ttl_seconds=300)
    intelligence_service = MarketNewsIntelligenceService(
        news_service=news_service,
        market_data_service=EmptyMarketDataService(),
    )

    assert news_service.get_latest(limit=3)["degraded"] is False
    session.fail_flash = True
    session.fail_public = True

    payload = intelligence_service.build_intelligence(limit=3)

    assert payload["degraded"] is True
    assert payload["warnings"]
    assert payload["keywords"][0]["keyword"] == "computing"
    assert payload["sectorHints"] == []
