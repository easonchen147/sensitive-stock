from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..schemas.market import MarketNewsQuery, MarketQuotesQuery, MarketSectorsQuery
from ..services.deepseek_prediction import DeepSeekMarketPredictionService
from ..services.market_data import AkshareMarketDataService
from ..services.news_intelligence import (
    EastmoneyMarketNewsSource,
    Jin10NewsService,
    MarketNewsIntelligenceService,
    MultiSourceNewsService,
    SinaFinanceNewsSource,
)

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
            timeout=current_app.config["DEEPSEEK_TIMEOUT"],
            cache_ttl_seconds=current_app.config["DEEPSEEK_CACHE_TTL_SECONDS"],
        ),
        market_data_service=_get_market_data_service(),
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
    return jsonify(
        _get_news_intelligence_service().build_predictions(
            limit=query.limit,
            symbols=query.symbols,
        )
    )
