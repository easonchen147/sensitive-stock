from __future__ import annotations
from flask import Blueprint, current_app, jsonify, request
from ..schemas.stock_qa import StockQARequest
from ..services.stock_qa import StockQAService
from ..services.stock_detail import StockDetailService
from ..services.deepseek_prediction import DeepSeekMarketPredictionService

blueprint = Blueprint("qa", __name__)

def _get_qa_service():
    deepseek = DeepSeekMarketPredictionService(
        api_key=current_app.config.get("DEEPSEEK_API_KEY"),
        base_url=current_app.config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=current_app.config.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        thinking_type=current_app.config.get("DEEPSEEK_THINKING_TYPE", "enabled"),
        reasoning_effort=current_app.config.get("DEEPSEEK_REASONING_EFFORT", "high"),
        timeout=current_app.config.get("DEEPSEEK_TIMEOUT", 10),
    )
    return StockQAService(
        deepseek_service=deepseek,
        stock_detail_service=StockDetailService(),
    )

@blueprint.post("/qa/ask")
def ask_question():
    payload = request.get_json(silent=True) or {}
    req = StockQARequest.model_validate(payload)
    result = _get_qa_service().answer(question=req.question, symbols=req.symbols)
    return jsonify(result)
