from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..schemas.research import FactorAnalysisRequest
from ..services.factors import FactorAnalysisService

blueprint = Blueprint("factors", __name__)


def _get_factor_service():
    factory = current_app.config.get("FACTOR_ANALYSIS_SERVICE_FACTORY") or FactorAnalysisService
    return factory() if callable(factory) else factory


@blueprint.get("/factors")
def factors_overview():
    return jsonify(_get_factor_service().describe())


@blueprint.post("/factors/analyze")
def analyze_factors():
    payload = request.get_json(silent=True) or {}
    factor_request = FactorAnalysisRequest.model_validate(payload)
    return jsonify(_get_factor_service().analyze(factor_request))
