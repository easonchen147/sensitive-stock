from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..schemas.research import DiagnosisRequest
from ..services.diagnosis import DiagnosisService

blueprint = Blueprint("diagnosis", __name__)


def _get_diagnosis_service():
    factory = current_app.config.get("DIAGNOSIS_SERVICE_FACTORY") or DiagnosisService
    return factory() if callable(factory) else factory


@blueprint.get("/diagnosis")
def diagnosis_overview():
    return jsonify(_get_diagnosis_service().describe())


@blueprint.post("/diagnosis/run")
def run_diagnosis():
    payload = request.get_json(silent=True) or {}
    diagnosis_request = DiagnosisRequest.model_validate(payload)
    return jsonify(_get_diagnosis_service().run(diagnosis_request))
