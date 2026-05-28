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
from ..schemas.stock_detail import (
    FinancialSummaryQuery,
    KlineQuery,
    StockDetailQuery,
    StockNewsQuery,
)
from ..services.deepseek_prediction import DeepSeekMarketPredictionService
from ..services.market_data import AkshareMarketDataService
from ..services.stock_detail import StockDetailService
from ..services.news_intelligence import (
    ClsTelegraphNewsSource,
    CninfoDisclosureNewsSource,
    EastmoneyMarketNewsSource,
    Jin10NewsService,
    MarketNewsIntelligenceService,
    MultiSourceNewsService,
    SinaFinanceNewsSource,
    StcnArticleListSource,
    TwentyOneJingjiArticleListSource,
)
from ..services.prediction_history import PredictionHistoryService

blueprint = Blueprint("market", __name__)


def _get_market_data_service():
    factory = current_app.config.get("MARKET_DATA_SERVICE_FACTORY") or AkshareMarketDataService
    if factory is not AkshareMarketDataService:
        return factory() if callable(factory) else factory
    return AkshareMarketDataService(
        timeout=current_app.config["HTTP_TIMEOUT"],
        tickflow_api_key=current_app.config["TICKFLOW_API_KEY"],
        tickflow_base_url=current_app.config["TICKFLOW_BASE_URL"],
        tickflow_timeout=current_app.config["TICKFLOW_TIMEOUT"],
    )


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
    extra_sources = [
        EastmoneyMarketNewsSource(
            url=current_app.config["EASTMONEY_NEWS_URL"],
            timeout=current_app.config["HTTP_TIMEOUT"],
        ),
        SinaFinanceNewsSource(
            url=current_app.config["SINA_FINANCE_NEWS_URL"],
            timeout=current_app.config["HTTP_TIMEOUT"],
        ),
    ]

    cls_url = str(current_app.config.get("CLS_TELEGRAPH_URL") or "").strip()
    if cls_url:
        extra_sources.append(
            ClsTelegraphNewsSource(
                url=cls_url,
                timeout=current_app.config["HTTP_TIMEOUT"],
            )
        )

    stcn_url = str(current_app.config.get("STCN_NEWS_URL") or "").strip()
    if stcn_url:
        extra_sources.append(
            StcnArticleListSource(
                url=stcn_url,
                timeout=current_app.config["HTTP_TIMEOUT"],
            )
        )

    jingji21_url = str(current_app.config.get("JINGJI21_CAPITAL_NEWS_URL") or "").strip()
    if jingji21_url:
        extra_sources.append(
            TwentyOneJingjiArticleListSource(
                url=jingji21_url,
                timeout=current_app.config["HTTP_TIMEOUT"],
            )
        )

    cninfo_disclosure_url = str(current_app.config.get("CNINFO_DISCLOSURE_URL") or "").strip()
    cninfo_referer_url = str(
        current_app.config.get("CNINFO_DISCLOSURE_REFERER_URL") or ""
    ).strip()
    cninfo_static_base_url = str(current_app.config.get("CNINFO_STATIC_BASE_URL") or "").strip()
    if cninfo_disclosure_url and cninfo_static_base_url:
        extra_sources.extend(
            [
                CninfoDisclosureNewsSource(
                    url=cninfo_disclosure_url,
                    referer_url=cninfo_referer_url,
                    static_base_url=cninfo_static_base_url,
                    column="szse_latest",
                    market_name="深市",
                    source="cninfo_szse_disclosures",
                    timeout=current_app.config["HTTP_TIMEOUT"],
                ),
                CninfoDisclosureNewsSource(
                    url=cninfo_disclosure_url,
                    referer_url=cninfo_referer_url,
                    static_base_url=cninfo_static_base_url,
                    column="sse_latest",
                    market_name="沪市",
                    source="cninfo_sse_disclosures",
                    timeout=current_app.config["HTTP_TIMEOUT"],
                ),
                CninfoDisclosureNewsSource(
                    url=cninfo_disclosure_url,
                    referer_url=cninfo_referer_url,
                    static_base_url=cninfo_static_base_url,
                    column="bj_latest",
                    market_name="北交所",
                    source="cninfo_bse_disclosures",
                    timeout=current_app.config["HTTP_TIMEOUT"],
                ),
            ]
        )

    return MarketNewsIntelligenceService(
        news_service=MultiSourceNewsService(
            primary_service=primary_news_service,
            extra_sources=extra_sources,
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


def _get_stock_detail_service():
    return StockDetailService()


@blueprint.get("/market/stock/<symbol>/detail")
def stock_detail(symbol: str):
    service = _get_stock_detail_service()
    return jsonify(service.get_stock_detail(symbol))


@blueprint.get("/market/stock/<symbol>/kline")
def stock_kline(symbol: str):
    query_params = {**request.args.to_dict(flat=True), "symbol": symbol}
    query = KlineQuery.model_validate(query_params)
    service = _get_stock_detail_service()
    return jsonify(
        service.get_kline_data(
            symbol=query.symbol,
            period=query.period,
            start_date=query.start_date,
            end_date=query.end_date,
        )
    )


@blueprint.get("/market/stock/<symbol>/financials")
def stock_financials(symbol: str):
    service = _get_stock_detail_service()
    return jsonify(service.get_financial_summary(symbol))


@blueprint.get("/market/stock/<symbol>/news")
def stock_news(symbol: str):
    query_params = {**request.args.to_dict(flat=True), "symbol": symbol}
    query = StockNewsQuery.model_validate(query_params)
    service = _get_stock_detail_service()
    return jsonify(service.get_stock_news(symbol, limit=query.limit))


@blueprint.get("/market/news/categories")
def market_news_categories():
    from ..services.news_intelligence import NEWS_CATEGORIES
    return jsonify({
        "categories": [
            {"id": cat["categoryId"], "label": cat["label"]}
            for cat in NEWS_CATEGORIES
        ]
    })
