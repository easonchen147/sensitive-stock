from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..errors import APIError
from ..schemas.watchlist import WatchlistAddRequest, WatchlistUpdateRequest
from ..services.watchlist import WatchlistService

blueprint = Blueprint("watchlist", __name__)


def _service() -> WatchlistService:
    return WatchlistService()


def _username() -> str:
    principal = getattr(g, "auth_principal", None)
    if principal is None:
        raise APIError(
            code="authentication_required",
            message="A valid bearer token is required.",
            status_code=401,
        )
    return principal["username"]


@blueprint.get("/watchlist")
def get_watchlist():
    items = _service().get_watchlist(_username())
    return jsonify({"items": items})


@blueprint.post("/watchlist")
def add_watchlist_item():
    payload = request.get_json(silent=True) or {}
    add_request = WatchlistAddRequest.model_validate(payload)
    try:
        item = _service().add_item(_username(), add_request.model_dump())
    except ValueError as error:
        raise APIError(
            code="duplicate_symbol",
            message=str(error),
            status_code=409,
        ) from error
    return jsonify(item), 201


@blueprint.put("/watchlist/<symbol>")
def update_watchlist_item(symbol: str):
    payload = request.get_json(silent=True) or {}
    update_request = WatchlistUpdateRequest.model_validate(payload)
    updates = {k: v for k, v in update_request.model_dump().items() if v is not None}
    try:
        item = _service().update_item(_username(), symbol, updates)
    except ValueError as error:
        raise APIError(
            code="symbol_not_found",
            message=str(error),
            status_code=404,
        ) from error
    return jsonify(item)


@blueprint.delete("/watchlist/<symbol>")
def remove_watchlist_item(symbol: str):
    removed = _service().remove_item(_username(), symbol)
    if not removed:
        raise APIError(
            code="symbol_not_found",
            message=f"Symbol '{symbol}' not found in watchlist.",
            status_code=404,
        )
    return jsonify({"ok": True})
