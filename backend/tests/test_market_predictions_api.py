from __future__ import annotations

from app import create_app
from tests.auth_helpers import auth_test_config, issue_auth_headers


class StubMarketDataService:
    def get_market_overview(self) -> dict:
        return {"primarySource": "akshare", "fallbackSources": [], "routes": {}}

    def list_sector_catalog(self) -> list[dict]:
        return []


class StubNewsPredictionService:
    def __init__(self) -> None:
        self.seen_limit: int | None = None
        self.seen_symbols: list[str] | None = None

    def build_predictions(self, limit: int = 100, symbols: list[str] | None = None) -> dict:
        self.seen_limit = limit
        self.seen_symbols = symbols or []
        return {
            "source": "multi_source_news",
            "requestedLimit": limit,
            "degraded": True,
            "warnings": ["DeepSeek API key is not configured."],
            "channels": [
                {
                    "name": "Jin10",
                    "source": "jin10_flash_api",
                    "status": "ok",
                    "itemCount": 1,
                    "warnings": [],
                }
            ],
            "items": [
                {
                    "id": "news-1",
                    "publishedAt": "2026-05-21 10:00:00",
                    "title": "AI infrastructure demand expands",
                    "content": "Computing and cooling supply chains remain active.",
                    "important": True,
                    "tags": ["AI", "cooling"],
                    "source": "jin10",
                }
            ],
            "keywords": [{"keyword": "AI", "count": 3, "coverage": 1}],
            "sectorHints": [
                {
                    "name": "AI infrastructure",
                    "boardType": "concept",
                    "score": 4,
                    "matchedKeywords": ["AI"],
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
                "keywordCount": 1,
                "sectorHintCount": 1,
                "symbolCount": len(symbols or []),
                "warnings": ["DeepSeek API key is not configured."],
            },
            "predictions": [
                {
                    "targetType": "sector",
                    "target": "AI infrastructure",
                    "direction": "bullish",
                    "confidence": 0.62,
                    "score": 4,
                    "horizon": "1-3 trading days",
                    "drivers": ["AI"],
                    "sourceIds": ["news-1"],
                }
            ],
            "predictionSummary": "stub prediction",
            "riskNotes": ["Validate with backtests."],
            "backtestHandoff": {
                "endpoint": "/api/v1/backtests/run",
                "suggestedPreset": "event_theme_momentum",
                "symbols": symbols or [],
                "defaultParams": {"lookback_window": 20},
            },
        }


def test_market_news_predictions_endpoint_returns_prediction_payload() -> None:
    service = StubNewsPredictionService()
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

    response = client.get(
        "/api/v1/market/news/predictions?limit=20&symbols=000001,600000",
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert service.seen_limit == 20
    assert service.seen_symbols == ["000001", "600000"]
    assert payload["predictionMetadata"]["provider"] == "local_heuristic"
    assert payload["predictionMetadata"]["schemaVersion"] == "market-prediction-json-v1"
    assert payload["predictions"][0]["target"] == "AI infrastructure"
    assert payload["backtestHandoff"]["suggestedPreset"] == "event_theme_momentum"
    assert payload["backtestHandoff"]["symbols"] == ["000001", "600000"]
