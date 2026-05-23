from __future__ import annotations

from app import create_app
from tests.auth_helpers import auth_test_config, issue_auth_headers


class StubMarketDataService:
    def __init__(self) -> None:
        self.seen_symbols: list[str] | None = None
        self.seen_limit: int | None = None

    def get_market_overview(self) -> dict:
        return {
            "primarySource": "akshare",
            "fallbackSources": ["tushare", "sina_direct"],
            "routes": {
                "quotes": "/api/v1/market/quotes",
                "sectors": "/api/v1/market/sectors",
                "news": "/api/v1/market/news",
                "newsIntelligence": "/api/v1/market/news/intelligence",
            },
        }

    def get_quotes(self, symbols: list[str]) -> dict:
        self.seen_symbols = symbols
        return {
            "source": "akshare",
            "items": [
                {
                    "symbol": symbol,
                    "name": f"股票{symbol}",
                    "price": 10.0,
                    "changePercent": 1.5,
                }
                for symbol in symbols
            ],
        }

    def get_hot_sectors(self, limit: int = 5, sector_type: str = "concept") -> dict:
        self.seen_limit = limit
        return {
            "source": "akshare",
            "sectorType": sector_type,
            "items": [
                {
                    "name": "算力",
                    "type": sector_type,
                    "changePercent": 3.8,
                    "source": "akshare",
                }
            ],
        }


class StubNewsIntelligenceService:
    def __init__(self) -> None:
        self.seen_limit: int | None = None

    def get_latest(self, limit: int = 100) -> dict:
        self.seen_limit = limit
        return {
            "source": "jin10_flash_api",
            "requestedLimit": limit,
            "degraded": False,
            "items": [
                {
                    "id": "news-1",
                    "publishedAt": "2026-03-31 23:37:42",
                    "title": "算力概念继续活跃",
                    "content": "算力和液冷方向盘中拉升。",
                    "important": True,
                    "tags": ["算力", "液冷"],
                }
            ],
        }

    def build_intelligence(self, limit: int = 100) -> dict:
        self.seen_limit = limit
        return {
            "source": "jin10_flash_api",
            "requestedLimit": limit,
            "degraded": False,
            "items": [
                {
                    "id": "news-1",
                    "publishedAt": "2026-03-31 23:37:42",
                    "title": "算力概念继续活跃",
                    "content": "算力和液冷方向盘中拉升。",
                    "important": True,
                    "tags": ["算力", "液冷"],
                }
            ],
            "keywords": [
                {"keyword": "算力", "count": 3},
                {"keyword": "液冷", "count": 2},
            ],
            "sectorHints": [
                {
                    "name": "算力租赁",
                    "boardType": "concept",
                    "score": 3,
                    "matchedKeywords": ["算力"],
                }
            ],
        }

    def build_predictions(
        self,
        limit: int = 100,
        symbols: list[str] | None = None,
        thinking_type: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict:
        self.seen_limit = limit
        return {
            **self.build_intelligence(limit=limit),
            "channels": [
                {
                    "name": "Jin10",
                    "source": "jin10_flash_api",
                    "status": "ok",
                    "itemCount": 1,
                    "warnings": [],
                }
            ],
            "predictionMetadata": {
                "provider": "local_heuristic",
                "model": "keyword-sector-rules",
                "degraded": True,
                "cached": False,
                "schemaVersion": "market-prediction-json-v1",
                "cacheKey": "cache-1",
                "inputDigest": "digest-1",
                "newsItemCount": 1,
                "keywordCount": 2,
                "sectorHintCount": 1,
                "symbolCount": len(symbols or []),
                "warnings": ["DeepSeek API key is not configured."],
            },
            "predictions": [
                {
                    "targetType": "sector",
                    "target": "绠楀姏绉熻祦",
                    "direction": "bullish",
                    "confidence": 0.6,
                    "score": 3,
                    "horizon": "1-3 trading days",
                    "drivers": ["绠楀姏"],
                    "sourceIds": ["news-1"],
                }
            ],
            "predictionSummary": "测试预测摘要",
            "riskNotes": ["建议继续用量化回测验证。"],
            "backtestHandoff": {
                "endpoint": "/api/v1/backtests/run",
                "suggestedPreset": "event_theme_momentum",
                "symbols": symbols or [],
                "defaultParams": {"lookback_window": 20},
                "notes": [
                    "可将这里的候选标的直接交给量化回测，用事件主题动量策略做二次验证。",
                    "预测结果只用于研究判断与复盘，不应被视为直接交易指令。",
                ],
            },
        }


def test_market_overview_endpoint_returns_real_service_payload() -> None:
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "MARKET_DATA_SERVICE_FACTORY": lambda: StubMarketDataService(),
            "NEWS_INTELLIGENCE_SERVICE_FACTORY": lambda: StubNewsIntelligenceService(),
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get("/api/v1/market", headers=headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["primarySource"] == "akshare"
    assert payload["fallbackSources"] == ["tushare", "sina_direct"]
    assert payload["routes"]["newsIntelligence"] == "/api/v1/market/news/intelligence"


def test_market_quotes_endpoint_normalizes_symbol_list() -> None:
    service = StubMarketDataService()
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "MARKET_DATA_SERVICE_FACTORY": lambda: service,
            "NEWS_INTELLIGENCE_SERVICE_FACTORY": lambda: StubNewsIntelligenceService(),
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get("/api/v1/market/quotes?symbols=000001,600000", headers=headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert service.seen_symbols == ["000001", "600000"]
    assert payload["items"][0]["symbol"] == "000001"
    assert payload["source"] == "akshare"


def test_market_news_intelligence_endpoint_returns_structured_payload() -> None:
    service = StubNewsIntelligenceService()
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "MARKET_DATA_SERVICE_FACTORY": lambda: StubMarketDataService(),
            "NEWS_INTELLIGENCE_SERVICE_FACTORY": lambda: service,
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get("/api/v1/market/news/intelligence?limit=100", headers=headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert service.seen_limit == 100
    assert payload["requestedLimit"] == 100
    assert payload["keywords"][0]["keyword"] == "算力"
    assert payload["sectorHints"][0]["name"] == "算力租赁"
