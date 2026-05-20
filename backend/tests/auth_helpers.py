from __future__ import annotations

from flask.testing import FlaskClient

TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "SensitiveStock-Internal-MVP"
TEST_AUTH_SECRET = "test-auth-secret"


def auth_test_config() -> dict[str, object]:
    return {
        "AUTH_ADMIN_USERNAME": TEST_ADMIN_USERNAME,
        "AUTH_ADMIN_PASSWORD": TEST_ADMIN_PASSWORD,
        "AUTH_TOKEN_SECRET": TEST_AUTH_SECRET,
        "AUTH_TOKEN_TTL_SECONDS": 3600,
    }


def issue_auth_headers(client: FlaskClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200, response.get_json()
    payload = response.get_json()
    return {
        "Authorization": f"Bearer {payload['accessToken']}",
    }
