from __future__ import annotations

from flask import Blueprint, jsonify

from ..services.capabilities import list_capabilities

blueprint = Blueprint("capabilities", __name__)


@blueprint.get("/capabilities")
def capabilities():
    return jsonify({"items": list_capabilities()})
