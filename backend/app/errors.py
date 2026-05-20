from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import Flask, jsonify
from pydantic import ValidationError


@dataclass
class APIError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: Any = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details is not None:
            payload["details"] = self.details
        return payload


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):  # type: ignore[override]
        return jsonify({"error": error.to_dict()}), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):  # type: ignore[override]
        messages = []
        details = []
        for item in error.errors():
            path = ".".join(str(part) for part in item.get("loc", []))
            message = item.get("msg", "invalid value")
            messages.append(f"{path}: {message}" if path else message)
            sanitized_item = dict(item)
            if "ctx" in sanitized_item and isinstance(sanitized_item["ctx"], dict):
                sanitized_item["ctx"] = {
                    key: str(value) for key, value in sanitized_item["ctx"].items()
                }
            details.append(sanitized_item)

        api_error = APIError(
            code="validation_error",
            message="; ".join(messages),
            status_code=400,
            details=details,
        )
        return jsonify({"error": api_error.to_dict()}), api_error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):  # type: ignore[override]
        api_error = APIError(
            code="internal_error",
            message=str(error),
            status_code=500,
        )
        return jsonify({"error": api_error.to_dict()}), api_error.status_code
