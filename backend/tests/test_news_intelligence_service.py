from __future__ import annotations

import json

from app.services.news_intelligence import Jin10NewsService


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


class FakeSession:
    def __init__(
        self,
        flash_pages: list[list[dict]] | None = None,
        js_items: list[dict] | None = None,
        fail_flash: bool = False,
    ) -> None:
        self.flash_pages = flash_pages or []
        self.js_items = js_items or []
        self.fail_flash = fail_flash
        self.calls: list[tuple[str, dict | None]] = []
        self.page_index = 0

    def get(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        timeout: int | None = None,
    ):  # noqa: ANN001
        self.calls.append((url, params))
        if "get_flash_list" in url:
            if self.fail_flash:
                raise RuntimeError("flash api unavailable")
            page = self.flash_pages[self.page_index]
            self.page_index += 1
            return FakeResponse({"status": 200, "message": "OK", "data": page})

        if "flash_newest.js" in url:
            payload_text = json.dumps(self.js_items, ensure_ascii=False)
            return FakeResponse(text=f"var newest = {payload_text};")

        raise AssertionError(f"Unexpected url: {url}")


def _flash_item(item_id: int) -> dict:
    return {
        "id": f"20260331{item_id:08d}",
        "time": f"2026-03-31 10:{item_id % 60:02d}:00",
        "type": 0,
        "data": {
            "title": f"快讯{item_id}",
            "content": f"算力主题第{item_id}条",
            "source": "jin10",
            "source_link": "",
            "pic": "",
        },
        "important": 0,
        "tags": [],
        "channel": [1, 2, 3],
        "remark": [],
    }


def test_jin10_news_service_collects_latest_100_unique_items() -> None:
    page1 = [_flash_item(index) for index in range(1, 22)]
    page2 = [page1[-1], *[_flash_item(index) for index in range(22, 42)]]
    page3 = [page2[-1], *[_flash_item(index) for index in range(42, 62)]]
    page4 = [page3[-1], *[_flash_item(index) for index in range(62, 82)]]
    page5 = [page4[-1], *[_flash_item(index) for index in range(82, 103)]]
    session = FakeSession(flash_pages=[page1, page2, page3, page4, page5])
    service = Jin10NewsService(session=session)

    payload = service.get_latest(limit=100)

    assert payload["degraded"] is False
    assert payload["source"] == "jin10_flash_api"
    assert payload["requestedLimit"] == 100
    assert len(payload["items"]) == 100
    assert payload["items"][0]["id"] == "2026033100000001"
    assert any(params and params.get("max_time") for _, params in session.calls[1:])


def test_jin10_news_service_falls_back_to_public_feed_when_flash_api_fails() -> None:
    js_items = [_flash_item(index) for index in range(1, 4)]
    session = FakeSession(js_items=js_items, fail_flash=True)
    service = Jin10NewsService(session=session)

    payload = service.get_latest(limit=3)

    assert payload["degraded"] is True
    assert payload["source"] == "jin10_flash_newest_js"
    assert len(payload["items"]) == 3
    assert payload["items"][0]["title"] == "快讯1"
