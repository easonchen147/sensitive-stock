from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from ..openapi import build_openapi_document

blueprint = Blueprint("openapi", __name__)


@blueprint.get("/openapi.json")
def openapi_json():
    return jsonify(
        build_openapi_document(
            api_prefix=current_app.config["API_PREFIX"],
            title=f"{current_app.config['SERVICE_NAME']} API",
            version="0.1.0",
        )
    )
