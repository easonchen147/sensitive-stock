from __future__ import annotations

from app.services.deepseek_prediction import DeepSeekMarketPredictionService
from app.services.news_intelligence import MarketNewsIntelligenceService


class StaticNewsService:
    def get_latest(self, limit: int = 100) -> dict:
        return {
            "source": "static_news",
            "requestedLimit": limit,
            "degraded": False,
            "warnings": [],
            "items": [
                {
                    "id": "cninfo-1",
                    "publishedAt": "2026-05-24 09:30:00",
                    "title": "关于控股股东增持公司股份计划的公告",
                    "content": (
                        "市场 深市；证券简称 盐湖股份；证券代码 000792；"
                        "公告类型 股东增持；控股股东拟增持公司股份。"
                    ),
                    "important": True,
                    "tags": ["深市", "公告", "股东增持", "盐湖股份", "000792"],
                    "source": "cninfo_szse_disclosures",
                },
                {
                    "id": "cninfo-2",
                    "publishedAt": "2026-05-24 09:20:00",
                    "title": "关于收到交易所监管问询函的公告",
                    "content": (
                        "市场 沪市；证券简称 浦发银行；证券代码 600000；"
                        "公告类型 问询函；公司收到监管问询函。"
                    ),
                    "important": False,
                    "tags": ["沪市", "公告", "问询函", "浦发银行", "600000"],
                    "source": "cninfo_sse_disclosures",
                },
            ],
        }


class EmptyMarketDataService:
    def list_sector_catalog(self) -> list[dict]:
        return []


def test_event_hints_extract_structured_signals_from_disclosures() -> None:
    service = MarketNewsIntelligenceService(
        news_service=StaticNewsService(),
        market_data_service=EmptyMarketDataService(),
    )

    payload = service.build_intelligence(limit=20)

    hints = {hint["eventType"]: hint for hint in payload["eventHints"]}
    assert hints["shareholder_increase"]["signal"] == "bullish"
    assert hints["shareholder_increase"]["label"] == "股东增持"
    assert hints["shareholder_increase"]["relatedSymbols"] == ["000792"]
    assert hints["shareholder_increase"]["relatedNames"] == ["盐湖股份"]
    assert hints["regulatory_inquiry"]["signal"] == "bearish"
    assert hints["regulatory_inquiry"]["relatedSymbols"] == ["600000"]
    assert hints["regulatory_inquiry"]["sourceIds"] == ["cninfo-2"]


def test_event_hints_drive_heuristic_prediction_and_backtest_handoff() -> None:
    service = MarketNewsIntelligenceService(
        news_service=StaticNewsService(),
        market_data_service=EmptyMarketDataService(),
        prediction_service=DeepSeekMarketPredictionService(api_key=""),
    )

    payload = service.build_predictions(limit=20, symbols=[])

    assert payload["predictionMetadata"]["eventHintCount"] == 2
    assert payload["predictionMetadata"]["model"] == "event-keyword-sector-rules"
    assert payload["predictions"][0]["targetType"] == "symbol"
    assert payload["predictions"][0]["target"] == "000792 盐湖股份"
    assert payload["predictions"][0]["direction"] == "bullish"
    assert payload["backtestHandoff"]["symbols"] == ["000792", "600000"]
    assert "自动补全候选股票代码" in payload["backtestHandoff"]["notes"][0]


def test_explicit_symbols_override_event_handoff_suggestions() -> None:
    service = MarketNewsIntelligenceService(
        news_service=StaticNewsService(),
        market_data_service=EmptyMarketDataService(),
        prediction_service=DeepSeekMarketPredictionService(api_key=""),
    )

    payload = service.build_predictions(limit=20, symbols=["300750"])

    assert payload["backtestHandoff"]["symbols"] == ["300750"]
    assert "用户输入的观察标的" in payload["backtestHandoff"]["notes"][0]
