from __future__ import annotations

from app import create_app
from tests.auth_helpers import auth_test_config, issue_auth_headers


def test_health_endpoint_returns_service_metadata() -> None:
    app = create_app({"TESTING": True, "ENVIRONMENT": "testing", **auth_test_config()})
    client = app.test_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "service": "sensitive-stock-backend",
        "environment": "testing",
        "apiVersion": "v1",
        "status": "ok",
    }


def test_capability_inventory_lists_migrated_and_placeholder_modules() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get("/api/v1/capabilities", headers=headers)

    assert response.status_code == 200
    payload = response.get_json()
    items = {item["name"]: item for item in payload["items"]}
    assert items["backtest"]["status"] == "migrated"
    assert items["market"]["status"] == "migrated"
    assert items["screener"]["status"] == "migrated"
    assert items["screener"]["path"] == "/api/v1/screener/run"
