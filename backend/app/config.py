from __future__ import annotations

import os


class DefaultConfig:
    SERVICE_NAME = "sensitive-stock-backend"
    ENVIRONMENT = os.getenv("BACKEND_ENV", "development")
    API_PREFIX = os.getenv("BACKEND_API_PREFIX", "/api/v1")
    AUTH_ADMIN_USERNAME = os.getenv("BACKEND_AUTH_ADMIN_USERNAME", "admin")
    AUTH_ADMIN_PASSWORD = os.getenv("BACKEND_AUTH_ADMIN_PASSWORD", "SensitiveStock-Internal-MVP")
    AUTH_TOKEN_SECRET = os.getenv(
        "BACKEND_AUTH_TOKEN_SECRET",
        "sensitive-stock-internal-auth-secret",
    )
    AUTH_TOKEN_TTL_SECONDS = int(os.getenv("BACKEND_AUTH_TOKEN_TTL_SECONDS", "28800"))
    HTTP_TIMEOUT = int(os.getenv("BACKEND_HTTP_TIMEOUT", "10"))
    DEFAULT_MARKET_SECTOR_LIMIT = int(os.getenv("BACKEND_MARKET_SECTOR_LIMIT", "5"))
    DEFAULT_MARKET_NEWS_LIMIT = min(
        max(int(os.getenv("BACKEND_MARKET_NEWS_LIMIT", "100")), 1),
        100,
    )
    JIN10_FLASH_API_URL = os.getenv(
        "BACKEND_JIN10_FLASH_API_URL",
        "https://flash-api.jin10.com/get_flash_list",
    )
    JIN10_FALLBACK_URL = os.getenv(
        "BACKEND_JIN10_FALLBACK_URL",
        "https://www.jin10.com/flash_newest.js",
    )
    JIN10_APP_ID = os.getenv("BACKEND_JIN10_APP_ID", "bVBF4FyRTn5NJF5n")
    JIN10_API_VERSION = os.getenv("BACKEND_JIN10_API_VERSION", "1.0.0")
    JIN10_CHANNEL = os.getenv("BACKEND_JIN10_CHANNEL", "-8200")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    JSON_SORT_KEYS = False
