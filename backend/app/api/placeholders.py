from __future__ import annotations

from flask import Blueprint, jsonify

from ..errors import APIError
from ..services.capabilities import get_capability

blueprint = Blueprint("placeholders", __name__)

PLACEHOLDER_NAMES = (
    "screener",
    "diagnosis",
    "factors",
    "portfolio",
)


def _build_placeholder_handler(capability_name: str):
    def handler():
        capability = get_capability(capability_name)
        if capability is None:
            raise APIError(
                code="capability_not_found",
                message=f"Unknown capability: {capability_name}",
                status_code=404,
            )

        return jsonify(
            {
                **capability,
                "nextStep": capability["summary"],
            }
        )

    handler.__name__ = f"{capability_name}_placeholder"
    return handler


for placeholder_name in PLACEHOLDER_NAMES:
    blueprint.add_url_rule(
        f"/{placeholder_name}",
        view_func=_build_placeholder_handler(placeholder_name),
        methods=["GET"],
    )
