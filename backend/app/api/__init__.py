from __future__ import annotations

from flask import Flask

from .auth import blueprint as auth_blueprint
from .backtests import blueprint as backtests_blueprint
from .capabilities import blueprint as capabilities_blueprint
from .daily import blueprint as daily_blueprint
from .diagnosis import blueprint as diagnosis_blueprint
from .factors import blueprint as factors_blueprint
from .health import blueprint as health_blueprint
from .market import blueprint as market_blueprint
from .openapi import blueprint as openapi_blueprint
from .portfolio import blueprint as portfolio_blueprint
from .qa import blueprint as qa_blueprint
from .screener import blueprint as screener_blueprint
from .watchlist import blueprint as watchlist_blueprint


def register_blueprints(app: Flask) -> None:
    api_prefix = app.config["API_PREFIX"]
    for blueprint in (
        health_blueprint,
        openapi_blueprint,
        auth_blueprint,
        capabilities_blueprint,
        backtests_blueprint,
        market_blueprint,
        screener_blueprint,
        diagnosis_blueprint,
        factors_blueprint,
        daily_blueprint,
        portfolio_blueprint,
        qa_blueprint,
        watchlist_blueprint,
    ):
        app.register_blueprint(blueprint, url_prefix=api_prefix)
