from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request

from ..auth import get_auth_service
from ..errors import APIError
from ..schemas.auth import LoginRequest

blueprint = Blueprint("auth", __name__)


@blueprint.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    login_request = LoginRequest.model_validate(payload)

    auth_service = get_auth_service()
    if not auth_service.authenticate(login_request.username, login_request.password):
        raise APIError(
            code="authentication_failed",
            message="Invalid username or password.",
            status_code=401,
        )

    principal = auth_service.build_admin_principal()
    access_token = auth_service.issue_token(principal)
    return jsonify(
        {
            "accessToken": access_token,
            "tokenType": "Bearer",
            "expiresIn": current_app.config["AUTH_TOKEN_TTL_SECONDS"],
            "user": principal,
        }
    )


@blueprint.get("/auth/session")
def session():
    principal = getattr(g, "auth_principal", None)
    if principal is None:
        raise APIError(
            code="authentication_required",
            message="A valid bearer token is required.",
            status_code=401,
        )

    return jsonify(
        {
            "authenticated": True,
            "expiresIn": current_app.config["AUTH_TOKEN_TTL_SECONDS"],
            "user": principal,
        }
    )
