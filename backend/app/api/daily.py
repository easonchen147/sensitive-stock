from __future__ import annotations
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request
from ..schemas.daily import DailyRunRequest, DailyHistoryQuery
from ..services.daily_analysis import DailyAnalysisService
from ..services.market_data import AkshareMarketDataService
from ..services.stock_detail import StockDetailService
from ..services.deepseek_prediction import DeepSeekMarketPredictionService

blueprint = Blueprint("daily", __name__)


def _get_daily_service():
    deepseek = DeepSeekMarketPredictionService(
        api_key=current_app.config.get("DEEPSEEK_API_KEY"),
        base_url=current_app.config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=current_app.config.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        thinking_type=current_app.config.get("DEEPSEEK_THINKING_TYPE", "enabled"),
        reasoning_effort=current_app.config.get("DEEPSEEK_REASONING_EFFORT", "high"),
        timeout=current_app.config.get("DEEPSEEK_TIMEOUT", 10),
    )
    storage_path = Path(current_app.instance_path) / "daily_reports.jsonl"
    return DailyAnalysisService(
        market_data_service=AkshareMarketDataService(
            timeout=current_app.config["HTTP_TIMEOUT"],
            tickflow_api_key=current_app.config["TICKFLOW_API_KEY"],
            tickflow_base_url=current_app.config["TICKFLOW_BASE_URL"],
            tickflow_timeout=current_app.config["TICKFLOW_TIMEOUT"],
        ),
        stock_detail_service=StockDetailService(),
        deepseek_service=deepseek,
        storage_path=storage_path,
    )


@blueprint.post("/daily/run")
def run_daily():
    payload = request.get_json(silent=True) or {}
    req = DailyRunRequest.model_validate(payload)
    service = _get_daily_service()
    screen = service.run_daily_screen(universe=req.universe if req.universe else None)
    report = service.generate_report(screen)
    return jsonify(report)


@blueprint.get("/daily/latest")
def get_latest():
    service = _get_daily_service()
    report = service.get_latest_report()
    if report is None:
        return jsonify({"message": "暂无日报数据", "items": []})
    return jsonify(report)


@blueprint.get("/daily/history")
def get_history():
    query = DailyHistoryQuery.model_validate(request.args.to_dict(flat=True))
    service = _get_daily_service()
    return jsonify({"items": service.get_report_history(limit=query.limit)})
