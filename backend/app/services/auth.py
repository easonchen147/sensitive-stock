from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
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
        data_dir: str = "data",
    ) -> None:
        self._admin_username = admin_username
        self._admin_password = admin_password
        self._token_secret = token_secret
        self._token_ttl_seconds = token_ttl_seconds
        self._data_dir = Path(data_dir)
        self._users_path = self._data_dir / "users.json"

    @classmethod
    def from_config(cls) -> "AuthService":
        config = current_app.config
        return cls(
            admin_username=config["AUTH_ADMIN_USERNAME"],
            admin_password=config["AUTH_ADMIN_PASSWORD"],
            token_secret=config["AUTH_TOKEN_SECRET"],
            token_ttl_seconds=config["AUTH_TOKEN_TTL_SECONDS"],
        )

    # ── persistence helpers ─────────────────────────────────────────

    def _load_users(self) -> list[dict[str, Any]]:
        if not self._users_path.exists():
            return []
        with open(self._users_path, encoding="utf-8") as f:
            return json.load(f)

    def _save_users(self, users: list[dict[str, Any]]) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        with open(self._users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    # ── password hashing ────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
        return f"pbkdf2:sha256:600000${salt}${dk.hex()}"

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        parts = stored_hash.split("$")
        if len(parts) != 3 or not parts[0].startswith("pbkdf2:sha256:"):
            return False
        salt = parts[1]
        expected = parts[2]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
        return hmac.compare_digest(dk.hex(), expected)

    # ── user management ─────────────────────────────────────────────

    def register_user(
        self,
        username: str,
        password: str,
        display_name: str | None = None,
    ) -> dict[str, str]:
        users = self._load_users()
        if any(u["username"] == username for u in users):
            raise ValueError(f"User '{username}' already exists.")
        now = datetime.now(timezone.utc).isoformat()
        users.append(
            {
                "username": username,
                "password_hash": self._hash_password(password),
                "display_name": display_name or username,
                "role": "user",
                "created_at": now,
            }
        )
        self._save_users(users)
        return {"username": username, "display_name": display_name or username, "role": "user"}

    def authenticate(self, username: str, password: str) -> bool:
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                return self._verify_password(password, user["password_hash"])
        # fallback to env-based admin
        if self._users_path.exists():
            return False
        return hmac.compare_digest(username, self._admin_username) and hmac.compare_digest(
            password,
            self._admin_password,
        )

    def build_principal(self, username: str) -> dict[str, str]:
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                return AuthPrincipal(
                    username=username,
                    role=user.get("role", "user"),
                    scope="internal_mvp",
                ).to_dict()
        # fallback: env admin
        return AuthPrincipal(
            username=self._admin_username,
            role="admin",
            scope="internal_mvp",
        ).to_dict()

    def build_admin_principal(self) -> dict[str, str]:
        return AuthPrincipal(
            username=self._admin_username,
            role="admin",
            scope="internal_mvp",
        ).to_dict()

    def change_password(self, username: str, old_password: str, new_password: str) -> None:
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                if not self._verify_password(old_password, user["password_hash"]):
                    raise ValueError("Old password is incorrect.")
                user["password_hash"] = self._hash_password(new_password)
                self._save_users(users)
                return
        raise ValueError(f"User '{username}' not found.")

    def list_users(self, requesting_role: str) -> list[dict[str, Any]]:
        if requesting_role != "admin":
            raise PermissionError("Only admins can list users.")
        users = self._load_users()
        return [
            {
                "username": u["username"],
                "display_name": u.get("display_name", u["username"]),
                "role": u.get("role", "user"),
                "created_at": u.get("created_at", ""),
            }
            for u in users
        ]

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

        if not username or not role:
            raise AuthTokenError("The access token payload is invalid.")

        return {
            "username": username,
            "role": role,
            "scope": scope,
        }

    def _serializer(self) -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(self._token_secret, salt="sensitive-stock-auth")
