from __future__ import annotations

from app.services.news_intelligence import Jin10NewsService, MultiSourceNewsService


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeJin10Session:
    def __init__(self, page: list[dict]) -> None:
        self.page = page
        self.calls = 0

    def get(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        timeout: int | None = None,
    ) -> FakeResponse:
        self.calls += 1
        if self.calls > 1:
            return FakeResponse({"status": 200, "message": "OK", "data": []})
        return FakeResponse({"status": 200, "message": "OK", "data": self.page})


class StaticNewsSource:
    def __init__(
        self,
        items: list[dict],
        fail: bool = False,
        *,
        name: str = "Static Channel",
        source: str = "static_channel",
    ) -> None:
        self.items = items
        self.fail = fail
        self.name = name
        self.source = source

    def fetch(self, limit: int) -> list[dict]:
        if self.fail:
            raise RuntimeError("static channel unavailable")
        return self.items[:limit]


def _jin10_item(item_id: int, title: str, content: str) -> dict:
    return {
        "id": f"jin10-{item_id}",
        "time": f"2026-05-21 10:{item_id:02d}:00",
        "data": {"title": title, "content": content, "source_link": ""},
        "important": 0,
        "tags": [],
    }


def test_multi_source_news_service_merges_dedupes_and_reports_channels() -> None:
    primary = Jin10NewsService(
        session=FakeJin10Session(
            [
                _jin10_item(1, "AI cooling demand rises", "Cooling supply chain active."),
                _jin10_item(2, "Robotics orders improve", "Robotics demand improves."),
            ]
        )
    )
    duplicate = {
        "id": "external-1",
        "publishedAt": "2026-05-21 11:00:00",
        "title": "AI cooling demand rises",
        "content": "Cooling supply chain active.",
        "important": False,
        "tags": ["AI"],
        "sourceUrl": "",
        "source": "static_channel",
    }
    unique = {
        "id": "external-2",
        "publishedAt": "2026-05-21 11:05:00",
        "title": "Semiconductor equipment gains",
        "content": "Equipment makers lead the tape.",
        "important": True,
        "tags": ["semiconductor"],
        "sourceUrl": "https://example.test/news/2",
        "source": "static_channel",
    }
    service = MultiSourceNewsService(
        primary_service=primary,
        extra_sources=[StaticNewsSource([duplicate, unique])],
    )

    payload = service.get_latest(limit=10)

    assert payload["source"] == "multi_source_news"
    assert payload["sourceCount"] == 2
    assert len(payload["channels"]) == 2
    assert len(payload["items"]) == 3
    assert payload["sourceQuality"]["queriedChannels"] == 2
    assert payload["sourceQuality"]["succeededChannels"] == 2
    assert payload["sourceQuality"]["failedChannels"] == 0
    assert payload["sourceQuality"]["duplicateItems"] == 1
    assert payload["sourceQuality"]["qualityScore"] > 0
    assert payload["sourceQuality"]["coverageScore"] > 0
    assert payload["sourceQuality"]["reliabilityScore"] == 100
    assert payload["sourceQuality"]["qualityNotes"]
    assert payload["dedupeMetadata"]["strategy"] == "source-url-or-normalized-title-content"
    assert payload["dedupeMetadata"]["originalCount"] == 4
    assert payload["dedupeMetadata"]["uniqueCount"] == 3
    assert payload["dedupeMetadata"]["duplicateCount"] == 1
    assert any(item["title"] == "Semiconductor equipment gains" for item in payload["items"])


def test_multi_source_news_service_degrades_when_extra_channel_fails() -> None:
    primary = Jin10NewsService(
        session=FakeJin10Session(
            [_jin10_item(1, "AI cooling demand rises", "Cooling supply chain active.")]
        )
    )
    service = MultiSourceNewsService(
        primary_service=primary,
        extra_sources=[StaticNewsSource([], fail=True)],
    )

    payload = service.get_latest(limit=5)

    assert payload["degraded"] is True
    assert payload["channels"][1]["status"] == "failed"
    assert payload["sourceQuality"]["failedChannels"] == 1
    assert payload["sourceQuality"]["succeededChannels"] == 1
    assert payload["sourceQuality"]["qualityScore"] < 100
    assert "static channel unavailable" in payload["warnings"][0]


def test_multi_source_news_service_reports_extended_channel_coverage() -> None:
    primary = Jin10NewsService(
        session=FakeJin10Session(
            [_jin10_item(1, "AI cooling demand rises", "Cooling supply chain active.")]
        )
    )
    cls_item = {
        "id": "cls-1",
        "publishedAt": "2026-05-24 10:30:00",
        "title": "CLS telegraph headline",
        "content": "CLS telegraph headline",
        "important": True,
        "tags": ["telegraph"],
        "sourceUrl": "https://www.cls.cn/telegraph/1",
        "source": "cls_telegraph",
    }
    stcn_item = {
        "id": "stcn-1",
        "publishedAt": "",
        "title": "STCN article headline",
        "content": "STCN article headline",
        "important": False,
        "tags": [],
        "sourceUrl": "https://www.stcn.com/article/detail/1.html",
        "source": "stcn_headlines",
    }
    service = MultiSourceNewsService(
        primary_service=primary,
        extra_sources=[
            StaticNewsSource(
                [cls_item],
                name="CLS Telegraph",
                source="cls_telegraph",
            ),
            StaticNewsSource(
                [stcn_item],
                name="STCN",
                source="stcn_headlines",
            ),
            StaticNewsSource(
                [],
                fail=True,
                name="21st Century Business Herald",
                source="jingji21_capital_headlines",
            ),
        ],
    )

    payload = service.get_latest(limit=10)

    assert payload["degraded"] is True
    assert payload["sourceCount"] == 3
    assert payload["sourceQuality"]["queriedChannels"] == 4
    assert payload["sourceQuality"]["succeededChannels"] == 3
    assert payload["sourceQuality"]["failedChannels"] == 1
    assert set(payload["sourceQuality"]["sourceCoverage"]) == {
        "cls_telegraph",
        "jin10",
        "stcn_headlines",
    }
    assert any(channel["source"] == "cls_telegraph" for channel in payload["channels"])
    assert any(channel["source"] == "stcn_headlines" for channel in payload["channels"])
    assert any(
        channel["source"] == "jingji21_capital_headlines" and channel["status"] == "failed"
        for channel in payload["channels"]
    )


def test_multi_source_news_service_reports_cninfo_disclosure_channels() -> None:
    primary = Jin10NewsService(
        session=FakeJin10Session(
            [_jin10_item(1, "AI cooling demand rises", "Cooling supply chain active.")]
        )
    )
    szse_content = (
        "市场 深市；证券简称 盐湖股份；证券代码 000792；"
        "公告类型 日常经营；关于公司独立董事辞职的公告"
    )
    sse_content = (
        "市场 沪市；证券简称 浦发银行；证券代码 600000；"
        "公告类型 股东大会；2025年年度股东会决议公告"
    )
    szse_item = {
        "id": "cninfo-szse-1",
        "publishedAt": "2026-05-24 09:30:00",
        "title": "关于公司独立董事辞职的公告",
        "content": szse_content,
        "important": True,
        "tags": ["深市", "公告", "日常经营", "盐湖股份", "000792"],
        "sourceUrl": "https://static.cninfo.com.cn/finalpage/2026-05-24/1.PDF",
        "source": "cninfo_szse_disclosures",
    }
    sse_item = {
        "id": "cninfo-sse-1",
        "publishedAt": "2026-05-24 09:20:00",
        "title": "2025年年度股东会决议公告",
        "content": sse_content,
        "important": False,
        "tags": ["沪市", "公告", "股东大会", "浦发银行", "600000"],
        "sourceUrl": "https://static.cninfo.com.cn/finalpage/2026-05-24/2.PDF",
        "source": "cninfo_sse_disclosures",
    }
    service = MultiSourceNewsService(
        primary_service=primary,
        extra_sources=[
            StaticNewsSource(
                [szse_item],
                name="巨潮公告-深市",
                source="cninfo_szse_disclosures",
            ),
            StaticNewsSource(
                [sse_item],
                name="巨潮公告-沪市",
                source="cninfo_sse_disclosures",
            ),
            StaticNewsSource(
                [],
                fail=True,
                name="巨潮公告-北交所",
                source="cninfo_bse_disclosures",
            ),
        ],
    )

    payload = service.get_latest(limit=10)

    assert payload["degraded"] is True
    assert payload["sourceCount"] == 3
    assert payload["sourceQuality"]["queriedChannels"] == 4
    assert payload["sourceQuality"]["succeededChannels"] == 3
    assert payload["sourceQuality"]["failedChannels"] == 1
    assert set(payload["sourceQuality"]["sourceCoverage"]) == {
        "cninfo_szse_disclosures",
        "cninfo_sse_disclosures",
        "jin10",
    }
    assert any(
        channel["name"] == "巨潮公告-深市" and channel["source"] == "cninfo_szse_disclosures"
        for channel in payload["channels"]
    )
    assert any(
        channel["source"] == "cninfo_bse_disclosures" and channel["status"] == "failed"
        for channel in payload["channels"]
    )
