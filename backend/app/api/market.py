from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from ..errors import APIError
from ..schemas.market import (
    MarketNewsQuery,
    MarketQuotesQuery,
    MarketSectorsQuery,
    PredictionHistoryQuery,
)
from ..services.deepseek_prediction import DeepSeekMarketPredictionService
from ..services.market_data import AkshareMarketDataService
from ..services.news_intelligence import (
    EastmoneyMarketNewsSource,
    Jin10NewsService,
    MarketNewsIntelligenceService,
    MultiSourceNewsService,
    SinaFinanceNewsSource,
)
from ..services.prediction_history import PredictionHistoryService

blueprint = Blueprint("market", __name__)


def _get_market_data_service():
    factory = current_app.config.get("MARKET_DATA_SERVICE_FACTORY") or AkshareMarketDataService
    return factory() if callable(factory) else factory


def _get_news_intelligence_service():
    factory = current_app.config.get("NEWS_INTELLIGENCE_SERVICE_FACTORY")
    if factory is not None:
        return factory() if callable(factory) else factory

    primary_news_service = Jin10NewsService(
        flash_api_url=current_app.config["JIN10_FLASH_API_URL"],
        fallback_url=current_app.config["JIN10_FALLBACK_URL"],
        app_id=current_app.config["JIN10_APP_ID"],
        api_version=current_app.config["JIN10_API_VERSION"],
        channel=current_app.config["JIN10_CHANNEL"],
        timeout=current_app.config["HTTP_TIMEOUT"],
    )
    return MarketNewsIntelligenceService(
        news_service=MultiSourceNewsService(
            primary_service=primary_news_service,
            extra_sources=[
                EastmoneyMarketNewsSource(
                    url=current_app.config["EASTMONEY_NEWS_URL"],
                    timeout=current_app.config["HTTP_TIMEOUT"],
                ),
                SinaFinanceNewsSource(
                    url=current_app.config["SINA_FINANCE_NEWS_URL"],
                    timeout=current_app.config["HTTP_TIMEOUT"],
                ),
            ],
        ),
        prediction_service=DeepSeekMarketPredictionService(
            api_key=current_app.config["DEEPSEEK_API_KEY"],
            base_url=current_app.config["DEEPSEEK_BASE_URL"],
            model=current_app.config["DEEPSEEK_MODEL"],
            thinking_type=current_app.config["DEEPSEEK_THINKING_TYPE"],
            reasoning_effort=current_app.config["DEEPSEEK_REASONING_EFFORT"],
            timeout=current_app.config["DEEPSEEK_TIMEOUT"],
            cache_ttl_seconds=current_app.config["DEEPSEEK_CACHE_TTL_SECONDS"],
        ),
        market_data_service=_get_market_data_service(),
    )


def _get_prediction_history_service():
    factory = current_app.config.get("PREDICTION_HISTORY_SERVICE_FACTORY")
    if factory is not None:
        return factory() if callable(factory) else factory

    configured_path = str(current_app.config.get("PREDICTION_HISTORY_PATH") or "").strip()
    history_path = (
        Path(configured_path)
        if configured_path
        else Path(current_app.instance_path) / "prediction_history.jsonl"
    )
    return PredictionHistoryService(
        history_path,
        max_records=current_app.config["PREDICTION_HISTORY_LIMIT"],
    )


@blueprint.get("/market")
def market_overview():
    return jsonify(_get_market_data_service().get_market_overview())


@blueprint.get("/market/quotes")
def market_quotes():
    query = MarketQuotesQuery.model_validate(request.args.to_dict(flat=True))
    return jsonify(_get_market_data_service().get_quotes(query.symbols))


@blueprint.get("/market/sectors")
def market_sectors():
    query = MarketSectorsQuery.model_validate(request.args.to_dict(flat=True))
    return jsonify(
        _get_market_data_service().get_hot_sectors(
            limit=query.limit,
            sector_type=query.sector_type,
        )
    )


@blueprint.get("/market/news")
def market_news():
    query = MarketNewsQuery.model_validate(request.args.to_dict(flat=True))
    return jsonify(_get_news_intelligence_service().get_latest(limit=query.limit))


@blueprint.get("/market/news/intelligence")
def market_news_intelligence():
    query = MarketNewsQuery.model_validate(request.args.to_dict(flat=True))
    return jsonify(_get_news_intelligence_service().build_intelligence(limit=query.limit))


@blueprint.get("/market/news/predictions")
def market_news_predictions():
    query = MarketNewsQuery.model_validate(request.args.to_dict(flat=True))
    payload = _get_news_intelligence_service().build_predictions(
        limit=query.limit,
        symbols=query.symbols,
        thinking_type=query.thinking,
        reasoning_effort=query.reasoning_effort,
    )
    if payload.get("predictions"):
        stored_run = _get_prediction_history_service().store_run(payload)
        payload = {
            **payload,
            "runId": stored_run["runId"],
            "createdAt": stored_run["createdAt"],
            "predictions": stored_run["predictions"],
        }
    return jsonify(payload)


@blueprint.get("/market/news/prediction-history")
def market_prediction_history():
    query = PredictionHistoryQuery.model_validate(request.args.to_dict(flat=True))
    return jsonify(_get_prediction_history_service().list_runs(limit=query.limit))


@blueprint.get("/market/news/predictions/<run_id>")
def market_prediction_detail(run_id: str):
    run = _get_prediction_history_service().get_run(run_id)
    if run is None:
        raise APIError(
            code="prediction_run_not_found",
            message=f"未找到预测记录：{run_id}",
            status_code=404,
        )
    return jsonify(run)


@blueprint.get("/market/news/predictions/<run_id>/evaluate")
def market_prediction_evaluation(run_id: str):
    evaluation = _get_prediction_history_service().evaluate_run(
        run_id,
        _get_market_data_service(),
    )
    if evaluation is None:
        raise APIError(
            code="prediction_run_not_found",
            message=f"未找到预测记录：{run_id}",
            status_code=404,
        )
    return jsonify(evaluation)
