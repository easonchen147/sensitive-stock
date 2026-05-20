from __future__ import annotations

from flask import Blueprint, current_app, jsonify

blueprint = Blueprint("health", __name__)


@blueprint.get("/health")
def health() -> tuple[dict, int] | tuple[str, int]:
    return (
        jsonify(
            {
                "service": current_app.config["SERVICE_NAME"],
                "environment": current_app.config["ENVIRONMENT"],
                "apiVersion": current_app.config["API_PREFIX"].split("/")[-1],
                "status": "ok",
            }
        ),
        200,
    )
