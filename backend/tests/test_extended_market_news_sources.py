from __future__ import annotations

import json

from app.services.news_intelligence import (
    ClsTelegraphNewsSource,
    StcnArticleListSource,
    TwentyOneJingjiArticleListSource,
)


class FakeTextResponse:
    def __init__(
        self,
        text: str,
        *,
        status_code: int = 200,
        apparent_encoding: str = "utf-8",
        encoding: str = "utf-8",
    ) -> None:
        self.text = text
        self.status_code = status_code
        self.apparent_encoding = apparent_encoding
        self.encoding = encoding

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeHtmlSession:
    def __init__(self, response: FakeTextResponse) -> None:
        self.response = response

    def get(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        timeout: int | None = None,
    ) -> FakeTextResponse:
        return self.response


def test_cls_telegraph_source_parses_next_data_items() -> None:
    body = "【算力板块延续强势】财联社5月24日电，液冷和服务器方向盘中继续活跃。"
    payload = {
        "props": {
            "pageProps": {
                "telegraphList": [
                    {
                        "id": 2379943,
                        "title": "算力板块延续强势",
                        "content": body,
                        "brief": body,
                        "ctime": 1779589800,
                        "level": "A",
                        "shareurl": "https://api3.cls.cn/share/article/2379943?os=web",
                        "tags": ["算力", "液冷"],
                    }
                ]
            }
        }
    }
    html = (
        "<html><body>"
        '<script id="__NEXT_DATA__" type="application/json">'
        f"{json.dumps(payload, ensure_ascii=False)}"
        "</script></body></html>"
    )
    service = ClsTelegraphNewsSource(session=FakeHtmlSession(FakeTextResponse(html)))

    items = service.fetch(limit=5)

    assert len(items) == 1
    assert items[0]["id"] == "cls:2379943"
    assert items[0]["publishedAt"] == "2026-05-24 10:30:00"
    assert items[0]["title"] == "算力板块延续强势"
    assert items[0]["important"] is True
    assert items[0]["tags"] == ["算力", "液冷"]
    assert items[0]["source"] == "cls_telegraph"
    assert items[0]["sourceUrl"].startswith("https://api3.cls.cn/share/article/2379943")


def test_stcn_source_extracts_article_detail_links() -> None:
    html = """
    <html>
      <body>
        <a href="/article/detail/3923893.html">
          习近平对山西长治市沁源县一煤矿瓦斯爆炸事故作出重要指示
        </a>
        <a href="/article/detail/3923894.html"><span>算力题材继续活跃</span></a>
        <a href="/article/list/kx.html">快讯</a>
      </body>
    </html>
    """
    service = StcnArticleListSource(session=FakeHtmlSession(FakeTextResponse(html)))

    items = service.fetch(limit=10)

    assert len(items) == 2
    assert items[0]["title"] == "习近平对山西长治市沁源县一煤矿瓦斯爆炸事故作出重要指示"
    assert items[0]["sourceUrl"] == "https://www.stcn.com/article/detail/3923893.html"
    assert items[1]["title"] == "算力题材继续活跃"
    assert all(item["source"] == "stcn_headlines" for item in items)


def test_21jingji_source_uses_first_non_empty_line_as_title() -> None:
    html = """
    <html>
      <body>
        <a href="https://www.21jingji.com/article/20260524/herald/abcdef123456.html">
          监管整治非法跨境券商，富途、老虎暴跌！七招拆解你的账户怎么办

          16小时前　　崔文静
        </a>
        <a href="https://www.21jingji.com/topic/market">专题页</a>
      </body>
    </html>
    """
    response = FakeTextResponse(html, encoding="ISO-8859-1", apparent_encoding="utf-8")
    service = TwentyOneJingjiArticleListSource(session=FakeHtmlSession(response))

    items = service.fetch(limit=10)

    assert len(items) == 1
    assert items[0]["title"] == "监管整治非法跨境券商，富途、老虎暴跌！七招拆解你的账户怎么办"
    assert items[0]["publishedAt"] == "2026-05-24"
    assert items[0]["source"] == "jingji21_capital_headlines"
    assert items[0]["sourceUrl"] == "https://www.21jingji.com/article/20260524/herald/abcdef123456.html"
