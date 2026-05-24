from __future__ import annotations

from file_env import get_backend_env_flag, get_backend_env_int, get_backend_env_value


class DefaultConfig:
    SERVICE_NAME = "sensitive-stock-backend"
    ENVIRONMENT = get_backend_env_value("BACKEND_ENV", "development")
    API_PREFIX = get_backend_env_value("BACKEND_API_PREFIX", "/api/v1")
    AUTH_ADMIN_USERNAME = get_backend_env_value("BACKEND_AUTH_ADMIN_USERNAME", "admin")
    AUTH_ADMIN_PASSWORD = get_backend_env_value(
        "BACKEND_AUTH_ADMIN_PASSWORD",
        "SensitiveStock-Internal-MVP",
    )
    AUTH_TOKEN_SECRET = get_backend_env_value(
        "BACKEND_AUTH_TOKEN_SECRET",
        "sensitive-stock-internal-auth-secret",
    )
    AUTH_TOKEN_TTL_SECONDS = get_backend_env_int("BACKEND_AUTH_TOKEN_TTL_SECONDS", 28800)
    HTTP_TIMEOUT = get_backend_env_int("BACKEND_HTTP_TIMEOUT", 10)
    DEFAULT_MARKET_SECTOR_LIMIT = get_backend_env_int("BACKEND_MARKET_SECTOR_LIMIT", 5)
    DEFAULT_MARKET_NEWS_LIMIT = min(
        max(get_backend_env_int("BACKEND_MARKET_NEWS_LIMIT", 100), 1),
        100,
    )
    MARKET_DATA_ENABLE_TICKFLOW = get_backend_env_flag(
        "BACKEND_MARKET_DATA_ENABLE_TICKFLOW",
        True,
    )
    MARKET_DATA_PREFER_TICKFLOW = get_backend_env_flag(
        "BACKEND_MARKET_DATA_PREFER_TICKFLOW",
        False,
    )
    TICKFLOW_API_KEY = get_backend_env_value("TICKFLOW_API_KEY", "")
    TICKFLOW_BASE_URL = get_backend_env_value("TICKFLOW_BASE_URL", "https://api.tickflow.org")
    TICKFLOW_FREE_BASE_URL = get_backend_env_value(
        "TICKFLOW_FREE_BASE_URL",
        "https://free-api.tickflow.org",
    )
    TICKFLOW_TIMEOUT = get_backend_env_int("BACKEND_TICKFLOW_TIMEOUT", HTTP_TIMEOUT)
    JIN10_FLASH_API_URL = get_backend_env_value(
        "BACKEND_JIN10_FLASH_API_URL",
        "https://flash-api.jin10.com/get_flash_list",
    )
    JIN10_FALLBACK_URL = get_backend_env_value(
        "BACKEND_JIN10_FALLBACK_URL",
        "https://www.jin10.com/flash_newest.js",
    )
    JIN10_APP_ID = get_backend_env_value("BACKEND_JIN10_APP_ID", "bVBF4FyRTn5NJF5n")
    JIN10_API_VERSION = get_backend_env_value("BACKEND_JIN10_API_VERSION", "1.0.0")
    JIN10_CHANNEL = get_backend_env_value("BACKEND_JIN10_CHANNEL", "-8200")
    EASTMONEY_NEWS_URL = get_backend_env_value(
        "BACKEND_EASTMONEY_NEWS_URL",
        "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns",
    )
    SINA_FINANCE_NEWS_URL = get_backend_env_value(
        "BACKEND_SINA_FINANCE_NEWS_URL",
        "https://zhibo.sina.com.cn/api/zhibo/feed",
    )
    CLS_TELEGRAPH_URL = get_backend_env_value(
        "BACKEND_CLS_TELEGRAPH_URL",
        "https://www.cls.cn/telegraph",
    )
    STCN_NEWS_URL = get_backend_env_value(
        "BACKEND_STCN_NEWS_URL",
        "https://www.stcn.com/",
    )
    JINGJI21_CAPITAL_NEWS_URL = get_backend_env_value(
        "BACKEND_21JINGJI_CAPITAL_NEWS_URL",
        "https://www.21jingji.com/channel/capital",
    )
    CNINFO_DISCLOSURE_URL = get_backend_env_value(
        "BACKEND_CNINFO_DISCLOSURE_URL",
        "https://www.cninfo.com.cn/new/disclosure",
    )
    CNINFO_DISCLOSURE_REFERER_URL = get_backend_env_value(
        "BACKEND_CNINFO_DISCLOSURE_REFERER_URL",
        "https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
    )
    CNINFO_STATIC_BASE_URL = get_backend_env_value(
        "BACKEND_CNINFO_STATIC_BASE_URL",
        "https://static.cninfo.com.cn/",
    )
    DEEPSEEK_API_KEY = get_backend_env_value("BACKEND_DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = get_backend_env_value(
        "BACKEND_DEEPSEEK_BASE_URL",
        "https://api.deepseek.com",
    )
    DEEPSEEK_MODEL = get_backend_env_value("BACKEND_DEEPSEEK_MODEL", "deepseek-v4-flash")
    DEEPSEEK_THINKING_TYPE = get_backend_env_value("BACKEND_DEEPSEEK_THINKING_TYPE", "enabled")
    DEEPSEEK_REASONING_EFFORT = get_backend_env_value(
        "BACKEND_DEEPSEEK_REASONING_EFFORT",
        "high",
    )
    DEEPSEEK_TIMEOUT = get_backend_env_int("BACKEND_DEEPSEEK_TIMEOUT", HTTP_TIMEOUT)
    DEEPSEEK_CACHE_TTL_SECONDS = get_backend_env_int(
        "BACKEND_DEEPSEEK_CACHE_TTL_SECONDS",
        300,
    )
    PREDICTION_HISTORY_PATH = get_backend_env_value("BACKEND_PREDICTION_HISTORY_PATH", "")
    PREDICTION_HISTORY_LIMIT = get_backend_env_int("BACKEND_PREDICTION_HISTORY_LIMIT", 200)
    CORS_ORIGINS = [
        origin.strip()
        for origin in get_backend_env_value(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:3000",
        ).split(",")
        if origin.strip()
    ]
    JSON_SORT_KEYS = False
