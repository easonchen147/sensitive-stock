from __future__ import annotations

from app import create_app
from tests.auth_helpers import (
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    auth_test_config,
)


def test_login_endpoint_returns_token_for_valid_admin_credentials() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["accessToken"]
    assert payload["tokenType"] == "Bearer"
    assert payload["user"]["username"] == TEST_ADMIN_USERNAME


def test_login_endpoint_rejects_invalid_credentials() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": TEST_ADMIN_USERNAME,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"]["code"] == "authentication_failed"


def test_protected_endpoints_reject_requests_without_token() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()

    response = client.get("/api/v1/capabilities")

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"]["code"] == "authentication_required"


def test_session_endpoint_returns_current_admin_for_valid_token() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD,
        },
    )
    access_token = login_response.get_json()["accessToken"]

    response = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["authenticated"] is True
    assert payload["user"]["username"] == TEST_ADMIN_USERNAME
