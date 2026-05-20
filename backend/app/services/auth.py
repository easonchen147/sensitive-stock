from __future__ import annotations

import hmac
from dataclasses import dataclass
from typing import Any

from flask import current_app
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer


class AuthTokenError(ValueError):
    pass


@dataclass(frozen=True)
class AuthPrincipal:
    username: str
    role: str
    scope: str

    def to_dict(self) -> dict[str, str]:
        return {
            "username": self.username,
            "role": self.role,
            "scope": self.scope,
        }


class AuthService:
    def __init__(
        self,
        *,
        admin_username: str,
        admin_password: str,
        token_secret: str,
        token_ttl_seconds: int,
    ) -> None:
        self._admin_username = admin_username
        self._admin_password = admin_password
        self._token_secret = token_secret
        self._token_ttl_seconds = token_ttl_seconds

    @classmethod
    def from_config(cls) -> "AuthService":
        config = current_app.config
        return cls(
            admin_username=config["AUTH_ADMIN_USERNAME"],
            admin_password=config["AUTH_ADMIN_PASSWORD"],
            token_secret=config["AUTH_TOKEN_SECRET"],
            token_ttl_seconds=config["AUTH_TOKEN_TTL_SECONDS"],
        )

    def authenticate(self, username: str, password: str) -> bool:
        return hmac.compare_digest(username, self._admin_username) and hmac.compare_digest(
            password,
            self._admin_password,
        )

    def build_admin_principal(self) -> dict[str, str]:
        return AuthPrincipal(
            username=self._admin_username,
            role="admin",
            scope="internal_mvp",
        ).to_dict()

    def issue_token(self, principal: dict[str, Any]) -> str:
        return self._serializer().dumps(principal)

    def verify_token(self, token: str) -> dict[str, str]:
        try:
            payload = self._serializer().loads(token, max_age=self._token_ttl_seconds)
        except (BadSignature, BadTimeSignature) as error:
            raise AuthTokenError("The access token is invalid or expired.") from error

        if not isinstance(payload, dict):
            raise AuthTokenError("The access token payload is invalid.")

        username = str(payload.get("username", "")).strip()
        role = str(payload.get("role", "")).strip()
        scope = str(payload.get("scope", "")).strip()
        if username != self._admin_username or role != "admin" or scope != "internal_mvp":
            raise AuthTokenError("The access token payload is invalid.")

        return {
            "username": username,
            "role": role,
            "scope": scope,
        }

    def _serializer(self) -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(self._token_secret, salt="sensitive-stock-auth")
