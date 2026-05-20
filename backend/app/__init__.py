from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from .api import register_blueprints
from .auth import register_auth_guard
from .config import DefaultConfig
from .errors import register_error_handlers


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    if config_overrides:
        app.config.update(config_overrides)

    CORS(
        app,
        resources={
            rf"{app.config['API_PREFIX']}/*": {
                "origins": app.config["CORS_ORIGINS"],
            }
        },
    )

    register_error_handlers(app)
    register_auth_guard(app)
    register_blueprints(app)
    return app
