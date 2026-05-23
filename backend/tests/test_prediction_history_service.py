from __future__ import annotations

from pathlib import Path

from app.services.prediction_history import PredictionHistoryService


class QuoteService:
    def get_quotes(self, symbols: list[str]) -> dict:
        return {
            "source": "stub",
            "items": [
                {"symbol": symbol, "changePercent": 1.25}
                for symbol in symbols
            ],
        }


def _payload() -> dict:
    return {
        "source": "multi_source_news",
        "requestedLimit": 20,
        "degraded": False,
        "warnings": [],
        "items": [{"id": "news-1", "title": "平安银行活跃", "content": "000001 放量。"}],
        "sourceQuality": {
            "qualityScore": 88,
            "coverageScore": 90,
            "freshnessScore": 80,
            "reliabilityScore": 100,
        },
        "dedupeMetadata": {"duplicateCount": 0},
        "predictionMetadata": {
            "provider": "local_heuristic",
            "model": "keyword-sector-rules",
            "degraded": True,
            "schemaVersion": "market-prediction-json-v1",
            "cacheKey": "cache-1",
            "inputDigest": "digest-1",
            "thinkingType": "enabled",
            "reasoningEffort": "high",
        },
        "predictions": [
            {
                "targetType": "symbol",
                "target": "000001",
                "direction": "bullish",
                "confidence": 0.7,
                "score": 7,
                "horizon": "1-3 个交易日",
                "drivers": ["放量"],
                "sourceIds": ["news-1"],
            },
            {
                "targetType": "theme",
                "target": "机器人",
                "direction": "neutral",
                "confidence": 0.4,
                "score": 3,
                "horizon": "1-3 个交易日",
                "drivers": ["主题热度"],
                "sourceIds": ["news-1"],
            },
        ],
        "riskNotes": ["需要回测验证。"],
        "backtestHandoff": {"endpoint": "/api/v1/backtests/run"},
    }


def test_prediction_history_stores_lists_and_reads_detail(tmp_path: Path) -> None:
    service = PredictionHistoryService(tmp_path / "history.jsonl")

    stored = service.store_run(_payload())
    history = service.list_runs(limit=5)
    detail = service.get_run(stored["runId"])

    assert stored["runId"].startswith("pred_")
    assert stored["predictions"][0]["predictionId"].startswith(stored["runId"])
    assert history["items"][0]["runId"] == stored["runId"]
    assert history["items"][0]["qualityScore"] == 88
    assert detail is not None
    assert detail["items"][0]["id"] == "news-1"


def test_prediction_history_skips_corrupt_lines(tmp_path: Path) -> None:
    path = tmp_path / "history.jsonl"
    path.write_text("{not-json}\n", encoding="utf-8")
    service = PredictionHistoryService(path)

    history = service.list_runs(limit=5)

    assert history["items"] == []
    assert history["metadata"]["degraded"] is True
    assert "无法解析" in history["metadata"]["warnings"][0]


def test_prediction_history_evaluates_symbol_predictions(tmp_path: Path) -> None:
    service = PredictionHistoryService(tmp_path / "history.jsonl")
    stored = service.store_run(_payload())

    evaluation = service.evaluate_run(stored["runId"], QuoteService())

    assert evaluation is not None
    assert evaluation["evaluationSummary"]["total"] == 2
    assert evaluation["evaluationSummary"]["hit"] == 1
    assert evaluation["evaluationSummary"]["pending"] == 1
    assert evaluation["evaluationItems"][0]["status"] == "hit"
