from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..schemas.research import ScreenerExportRequest, ScreenerRunRequest
from ..services.screener import ScreenerService

blueprint = Blueprint("screener", __name__)


def _get_screener_service():
    factory = current_app.config.get("SCREENER_SERVICE_FACTORY") or ScreenerService
    return factory() if callable(factory) else factory


@blueprint.get("/screener")
def screener_overview():
    return jsonify(_get_screener_service().list_templates())


@blueprint.post("/screener/run")
def run_screener():
    payload = request.get_json(silent=True) or {}
    screener_request = ScreenerRunRequest.model_validate(payload)
    return jsonify(_get_screener_service().run(screener_request))


@blueprint.post("/screener/export")
def export_screener():
    payload = request.get_json(silent=True) or {}
    export_request = ScreenerExportRequest.model_validate(payload)
    return jsonify(_get_screener_service().export(export_request))
