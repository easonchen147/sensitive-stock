from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..schemas.backtests import BacktestRunRequest
from ..services.backtests import AKQuantBacktestService

blueprint = Blueprint("backtests", __name__)


def _get_backtest_service():
    factory = current_app.config.get("BACKTEST_SERVICE_FACTORY") or AKQuantBacktestService
    return factory() if callable(factory) else factory


@blueprint.post("/backtests/run")
def run_backtests():
    payload = request.get_json(silent=True) or {}
    backtest_request = BacktestRunRequest.model_validate(payload)
    result = _get_backtest_service().run_batch(backtest_request)
    return jsonify(result)


@blueprint.get("/backtests/presets")
def list_backtest_presets():
    result = _get_backtest_service().list_presets()
    return jsonify(result)
