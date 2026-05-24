from __future__ import annotations

from app.services.news_intelligence import CninfoDisclosureNewsSource


class FakePostResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeCninfoSession:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    def post(
        self,
        url: str,
        headers: dict | None = None,
        data: dict | None = None,
        timeout: int | None = None,
    ) -> FakePostResponse:
        self.calls.append(
            {
                "url": url,
                "headers": headers or {},
                "data": data or {},
                "timeout": timeout,
            }
        )
        return FakePostResponse(self.payload)


def test_cninfo_disclosure_source_fetches_flat_announcements() -> None:
    payload = {
        "announcements": [
            {
                "announcementId": "1225328041",
                "announcementTitle": "关于公司独立董事辞职的公告",
                "announcementTime": 1779465600000,
                "adjunctUrl": "finalpage/2026-05-23/1225328041.PDF",
                "announcementTypeName": "日常经营",
                "secCode": "000792",
                "secName": "盐湖股份",
                "important": True,
            }
        ]
    }
    session = FakeCninfoSession(payload)
    service = CninfoDisclosureNewsSource(
        session=session,
        column="szse_latest",
        market_name="深市",
        source="cninfo_szse_disclosures",
    )

    items = service.fetch(limit=5)

    assert session.calls[0]["data"]["column"] == "szse_latest"
    assert session.calls[0]["data"]["clusterFlag"] == "false"
    assert session.calls[0]["data"]["pageSize"] == 5
    assert items[0]["id"] == "cninfo_szse_disclosures:1225328041"
    assert items[0]["publishedAt"] == "2026-05-23 00:00:00"
    assert items[0]["title"] == "关于公司独立董事辞职的公告"
    assert items[0]["important"] is True
    assert items[0]["sourceUrl"] == "https://static.cninfo.com.cn/finalpage/2026-05-23/1225328041.PDF"
    assert items[0]["tags"] == ["深市", "公告", "日常经营", "盐湖股份", "000792"]
    assert "证券简称 盐湖股份" in items[0]["content"]
    assert items[0]["source"] == "cninfo_szse_disclosures"


def test_cninfo_disclosure_source_flattens_classified_announcements_when_needed() -> None:
    payload = {
        "announcements": None,
        "classifiedAnnouncements": [
            [
                {
                    "announcementId": "9001",
                    "announcementTitle": "2025年年度股东会决议公告",
                    "announcementTime": 1779465600000,
                    "adjunctUrl": "finalpage/2026-05-23/9001.PDF",
                    "announcementTypeName": "股东大会",
                    "secCode": "600000",
                    "secName": "浦发银行",
                    "important": False,
                }
            ]
        ],
    }
    service = CninfoDisclosureNewsSource(
        session=FakeCninfoSession(payload),
        column="sse_latest",
        market_name="沪市",
        source="cninfo_sse_disclosures",
    )

    items = service.fetch(limit=3)

    assert len(items) == 1
    assert items[0]["id"] == "cninfo_sse_disclosures:9001"
    assert items[0]["tags"] == ["沪市", "公告", "股东大会", "浦发银行", "600000"]
    assert items[0]["sourceUrl"] == "https://static.cninfo.com.cn/finalpage/2026-05-23/9001.PDF"
