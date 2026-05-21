from __future__ import annotations

from flask import Flask, g, request

from .errors import APIError
from .services.auth import AuthService, AuthTokenError

PUBLIC_ENDPOINTS = {
    "auth.login",
    "health.health",
    "openapi.openapi_json",
}


def get_auth_service() -> AuthService:
    return AuthService.from_config()


def register_auth_guard(app: Flask) -> None:
    @app.before_request
    def require_authenticated_api():
        if request.method == "OPTIONS":
            return None

        api_prefix = app.config["API_PREFIX"]
        if not request.path.startswith(api_prefix):
            return None

        if request.endpoint is None or request.endpoint in PUBLIC_ENDPOINTS:
            return None

        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            raise APIError(
                code="authentication_required",
                message="A valid bearer token is required.",
                status_code=401,
            )

        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise APIError(
                code="authentication_required",
                message="A valid bearer token is required.",
                status_code=401,
            )

        try:
            g.auth_principal = get_auth_service().verify_token(token)
        except AuthTokenError as error:
            raise APIError(
                code="invalid_token",
                message=str(error),
                status_code=401,
            ) from error

        return None
