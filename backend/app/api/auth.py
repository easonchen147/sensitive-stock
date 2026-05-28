from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request

from ..auth import get_auth_service
from ..errors import APIError
from ..schemas.auth import LoginRequest, RegisterRequest

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

    principal = auth_service.build_principal(login_request.username)
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


@blueprint.post("/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    register_request = RegisterRequest.model_validate(payload)

    auth_service = get_auth_service()
    try:
        auth_service.register_user(
            register_request.username,
            register_request.password,
            register_request.display_name,
        )
    except ValueError as error:
        raise APIError(
            code="registration_failed",
            message=str(error),
            status_code=409,
        ) from error

    principal = auth_service.build_principal(register_request.username)
    access_token = auth_service.issue_token(principal)
    return jsonify(
        {
            "accessToken": access_token,
            "tokenType": "Bearer",
            "expiresIn": current_app.config["AUTH_TOKEN_TTL_SECONDS"],
            "user": principal,
        }
    )


@blueprint.post("/auth/change-password")
def change_password():
    payload = request.get_json(silent=True) or {}
    old_password = payload.get("old_password", "")
    new_password = payload.get("new_password", "")

    if not old_password or not new_password:
        raise APIError(
            code="validation_error",
            message="old_password and new_password are required.",
            status_code=400,
        )

    if len(new_password) < 6 or len(new_password) > 128:
        raise APIError(
            code="validation_error",
            message="new_password must be between 6 and 128 characters.",
            status_code=400,
        )

    principal = getattr(g, "auth_principal", None)
    if principal is None:
        raise APIError(
            code="authentication_required",
            message="A valid bearer token is required.",
            status_code=401,
        )

    auth_service = get_auth_service()
    try:
        auth_service.change_password(principal["username"], old_password, new_password)
    except ValueError as error:
        raise APIError(
            code="change_password_failed",
            message=str(error),
            status_code=400,
        ) from error

    return jsonify({"ok": True})
