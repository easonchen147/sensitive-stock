from __future__ import annotations

import json

from app.services.deepseek_prediction import DeepSeekMarketPredictionService


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, payload: dict | None = None, fail: bool = False) -> None:
        self.payload = payload or {}
        self.fail = fail
        self.calls: list[dict] = []

    def post(
        self,
        url: str,
        headers: dict | None = None,
        json: dict | None = None,
        timeout: int | None = None,
    ) -> FakeResponse:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        if self.fail:
            raise RuntimeError("deepseek unavailable")
        return FakeResponse(self.payload)


def _context() -> dict:
    return {
        "items": [
            {
                "id": "news-1",
                "title": "AI infrastructure demand expands",
                "content": "Computing and cooling supply chains remain active.",
                "tags": ["AI", "cooling"],
            }
        ],
        "keywords": [{"keyword": "AI", "count": 3, "coverage": 1}],
        "sector_hints": [
            {
                "name": "AI infrastructure",
                "boardType": "concept",
                "score": 4,
                "matchedKeywords": ["AI"],
            }
        ],
        "symbols": ["000001"],
    }


def test_prediction_uses_heuristic_when_deepseek_key_is_missing() -> None:
    service = DeepSeekMarketPredictionService(api_key="")
    context = _context()

    payload = service.predict(**context)

    assert payload["predictionMetadata"]["provider"] == "local_heuristic"
    assert payload["predictionMetadata"]["degraded"] is True
    assert payload["predictions"][0]["target"] == "AI infrastructure"
    assert payload["riskNotes"]


def test_prediction_calls_deepseek_v4_flash_and_parses_json_response() -> None:
    response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "AI infrastructure remains the strongest theme.",
                            "riskNotes": ["Validate with backtests."],
                            "predictions": [
                                {
                                    "targetType": "sector",
                                    "target": "AI infrastructure",
                                    "direction": "bullish",
                                    "confidence": 0.73,
                                    "score": 8.5,
                                    "horizon": "1-3 trading days",
                                    "drivers": ["AI", "cooling"],
                                    "sourceIds": ["news-1"],
                                }
                            ],
                        }
                    )
                }
            }
        ]
    }
    session = FakeSession(payload=response_payload)
    service = DeepSeekMarketPredictionService(api_key="test-key", session=session)
    context = _context()

    payload = service.predict(**context)

    assert session.calls[0]["url"] == "https://api.deepseek.com/chat/completions"
    assert session.calls[0]["json"]["model"] == "deepseek-v4-flash"
    assert session.calls[0]["json"]["response_format"] == {"type": "json_object"}
    assert "EXAMPLE JSON OUTPUT" in session.calls[0]["json"]["messages"][0]["content"]
    assert payload["predictionMetadata"]["provider"] == "deepseek"
    assert payload["predictionMetadata"]["degraded"] is False
    assert payload["predictionMetadata"]["schemaVersion"] == "market-prediction-json-v1"
    assert payload["predictionMetadata"]["cached"] is False
    assert payload["predictionMetadata"]["newsItemCount"] == 1
    assert payload["predictionMetadata"]["keywordCount"] == 1
    assert payload["predictionMetadata"]["sectorHintCount"] == 1
    assert payload["predictionMetadata"]["symbolCount"] == 1
    assert payload["predictionMetadata"]["inputDigest"]
    assert payload["predictions"][0]["confidence"] == 0.73


def test_prediction_reuses_cached_deepseek_payload_for_equivalent_context() -> None:
    response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "AI infrastructure remains active.",
                            "riskNotes": ["Validate with backtests."],
                            "predictions": [
                                {
                                    "targetType": "sector",
                                    "target": "AI infrastructure",
                                    "direction": "bullish",
                                    "confidence": 0.7,
                                    "score": 8,
                                    "horizon": "1-3 trading days",
                                    "drivers": ["AI"],
                                    "sourceIds": ["news-1"],
                                }
                            ],
                        }
                    )
                }
            }
        ]
    }
    session = FakeSession(payload=response_payload)
    service = DeepSeekMarketPredictionService(api_key="test-key", session=session)
    context = _context()

    first_payload = service.predict(**context)
    second_payload = service.predict(**context)

    assert len(session.calls) == 1
    assert first_payload["predictionMetadata"]["cached"] is False
    assert second_payload["predictionMetadata"]["cached"] is True
    assert second_payload["predictionMetadata"]["cacheKey"] == (
        first_payload["predictionMetadata"]["cacheKey"]
    )
    assert second_payload["predictions"] == first_payload["predictions"]


def test_prediction_cache_key_changes_when_symbols_change() -> None:
    response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "AI infrastructure remains active.",
                            "riskNotes": ["Validate with backtests."],
                            "predictions": [
                                {
                                    "targetType": "sector",
                                    "target": "AI infrastructure",
                                    "direction": "bullish",
                                    "confidence": 0.7,
                                    "score": 8,
                                    "horizon": "1-3 trading days",
                                    "drivers": ["AI"],
                                    "sourceIds": ["news-1"],
                                }
                            ],
                        }
                    )
                }
            }
        ]
    }
    session = FakeSession(payload=response_payload)
    service = DeepSeekMarketPredictionService(api_key="test-key", session=session)
    context = _context()

    first_payload = service.predict(**context)
    second_payload = service.predict(
        items=context["items"],
        keywords=context["keywords"],
        sector_hints=context["sector_hints"],
        symbols=["600000"],
    )

    assert len(session.calls) == 2
    assert first_payload["predictionMetadata"]["cacheKey"] != (
        second_payload["predictionMetadata"]["cacheKey"]
    )


def test_prediction_falls_back_when_deepseek_response_is_malformed() -> None:
    session = FakeSession(payload={"choices": [{"message": {"content": "not-json"}}]})
    service = DeepSeekMarketPredictionService(api_key="test-key", session=session)
    context = _context()

    payload = service.predict(**context)

    assert payload["predictionMetadata"]["provider"] == "local_heuristic"
    assert payload["predictionMetadata"]["degraded"] is True
    assert payload["predictionMetadata"]["schemaVersion"] == "market-prediction-json-v1"
    assert payload["predictionMetadata"]["cached"] is False
    assert payload["predictionMetadata"]["inputDigest"]
    assert "DeepSeek prediction failed" in payload["predictionMetadata"]["warnings"][0]
