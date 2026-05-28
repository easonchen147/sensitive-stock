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


@blueprint.post("/backtests/generate-strategy")
def generate_strategy():
    payload = request.get_json(silent=True) or {}
    from ..schemas.strategy import StrategyGenerateRequest
    from ..services.strategy_generator import StrategyGeneratorService
    from ..services.deepseek_prediction import DeepSeekMarketPredictionService

    req = StrategyGenerateRequest.model_validate(payload)

    deepseek_service = DeepSeekMarketPredictionService(
        api_key=current_app.config.get("DEEPSEEK_API_KEY"),
        base_url=current_app.config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=current_app.config.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        thinking_type=current_app.config.get("DEEPSEEK_THINKING_TYPE", "enabled"),
        reasoning_effort=current_app.config.get("DEEPSEEK_REASONING_EFFORT", "high"),
        timeout=current_app.config.get("DEEPSEEK_TIMEOUT", 10),
    )

    service = StrategyGeneratorService(deepseek_service=deepseek_service)
    result = service.generate(req.description)
    return jsonify(result)
