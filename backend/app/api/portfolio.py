from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..schemas.research import PortfolioOptimizationRequest
from ..services.portfolio import PortfolioOptimizationService

blueprint = Blueprint("portfolio", __name__)


def _get_portfolio_service():
    factory = current_app.config.get("PORTFOLIO_OPTIMIZATION_SERVICE_FACTORY") or (
        PortfolioOptimizationService
    )
    return factory() if callable(factory) else factory


@blueprint.get("/portfolio")
def portfolio_overview():
    return jsonify(_get_portfolio_service().describe())


@blueprint.post("/portfolio/optimize")
def optimize_portfolio():
    payload = request.get_json(silent=True) or {}
    portfolio_request = PortfolioOptimizationRequest.model_validate(payload)
    return jsonify(_get_portfolio_service().optimize(portfolio_request))
