from __future__ import annotations

from flask import Flask

from .auth import blueprint as auth_blueprint
from .backtests import blueprint as backtests_blueprint
from .capabilities import blueprint as capabilities_blueprint
from .health import blueprint as health_blueprint
from .market import blueprint as market_blueprint
from .placeholders import blueprint as placeholders_blueprint


def register_blueprints(app: Flask) -> None:
    api_prefix = app.config["API_PREFIX"]
    for blueprint in (
        health_blueprint,
        auth_blueprint,
        capabilities_blueprint,
        backtests_blueprint,
        market_blueprint,
        placeholders_blueprint,
    ):
        app.register_blueprint(blueprint, url_prefix=api_prefix)
