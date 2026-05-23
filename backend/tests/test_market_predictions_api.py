from __future__ import annotations

from pathlib import Path

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
        self.seen_thinking_type: str | None = None
        self.seen_reasoning_effort: str | None = None

    def build_predictions(
        self,
        limit: int = 100,
        symbols: list[str] | None = None,
        thinking_type: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict:
        self.seen_limit = limit
        self.seen_symbols = symbols or []
        self.seen_thinking_type = thinking_type
        self.seen_reasoning_effort = reasoning_effort
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
            "sourceQuality": {
                "queriedChannels": 1,
                "succeededChannels": 1,
                "degradedChannels": 0,
                "failedChannels": 0,
                "totalItems": 1,
                "uniqueItems": 1,
                "duplicateItems": 0,
                "sourceCoverage": ["jin10"],
                "qualityScore": 100,
                "coverageScore": 100,
                "freshnessScore": 5,
                "reliabilityScore": 100,
                "duplicatePressure": 0,
                "qualityNotes": ["测试来源质量。"],
            },
            "dedupeMetadata": {
                "strategy": "test",
                "originalCount": 1,
                "uniqueCount": 1,
                "duplicateCount": 0,
            },
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
                "thinkingType": thinking_type or "enabled",
                "reasoningEffort": reasoning_effort or "high",
                "requestMode": "heuristic",
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


def test_market_news_predictions_endpoint_returns_prediction_payload(tmp_path: Path) -> None:
    service = StubNewsPredictionService()
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "MARKET_DATA_SERVICE_FACTORY": lambda: StubMarketDataService(),
            "NEWS_INTELLIGENCE_SERVICE_FACTORY": lambda: service,
            "PREDICTION_HISTORY_PATH": str(tmp_path / "prediction_history.jsonl"),
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get(
        "/api/v1/market/news/predictions?limit=20&symbols=000001,600000&thinking=disabled&reasoningEffort=max",
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert service.seen_limit == 20
    assert service.seen_symbols == ["000001", "600000"]
    assert service.seen_thinking_type == "disabled"
    assert service.seen_reasoning_effort == "max"
    assert payload["runId"]
    assert payload["createdAt"]
    assert payload["predictions"][0]["predictionId"].startswith(payload["runId"])
    assert payload["predictionMetadata"]["provider"] == "local_heuristic"
    assert payload["predictionMetadata"]["schemaVersion"] == "market-prediction-json-v1"
    assert payload["predictions"][0]["target"] == "AI infrastructure"
    assert payload["backtestHandoff"]["suggestedPreset"] == "event_theme_momentum"
    assert payload["backtestHandoff"]["symbols"] == ["000001", "600000"]

    history_response = client.get("/api/v1/market/news/prediction-history", headers=headers)
    assert history_response.status_code == 200
    history_payload = history_response.get_json()
    assert history_payload["items"][0]["runId"] == payload["runId"]

    detail_response = client.get(
        f"/api/v1/market/news/predictions/{payload['runId']}",
        headers=headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.get_json()["runId"] == payload["runId"]
