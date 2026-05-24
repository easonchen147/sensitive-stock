from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import Literal

import akshare as ak
import pandas as pd
import requests

from file_env import get_backend_env_flag, get_backend_env_int, get_backend_env_value


class DataProviderError(RuntimeError):
    """Raised when the data provider cannot fulfill the request."""


@dataclass(frozen=True)
class HistoricalDataRequest:
    symbol: str  # Six-digit A-share code such as "600000"
    start_date: str  # "YYYY-MM-DD"
    end_date: str  # "YYYY-MM-DD"
    adjust: Literal["", "qfq", "hfq"] = "qfq"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "日期": "date",
        "时间": "date",
        "trade_date": "date",
        "开盘": "open",
        "开盘价": "open",
        "收盘": "close",
        "收盘价": "close",
        "最高": "high",
        "最高价": "high",
        "最低": "low",
        "最低价": "low",
        "成交量": "volume",
        "vol": "volume",
        "成交额": "amount",
        "成交金额": "amount",
        "trade_time": "date",
    }
    df = df.rename(columns=rename_map)
    expected_cols = ["date", "open", "high", "low", "close", "volume", "amount"]
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise DataProviderError(f"行情数据缺失字段: {missing_cols}")

    df = df[expected_cols].copy()
    df["date"] = pd.to_datetime(df["date"])
    numeric_cols = [col for col in expected_cols if col != "date"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna().sort_values("date")
    df = df.set_index("date")

    # Calculate pre_close
    df["pre_close"] = df["close"].shift(1)
    # Use open price as fallback for the first day's pre_close
    df["pre_close"] = df["pre_close"].fillna(df["open"])

    return df


def _env_flag(name: str, default: bool = False) -> bool:
    return get_backend_env_flag(name, default)


def _symbol_to_exchange_suffix(symbol: str) -> str:
    normalized = str(symbol).strip().upper()
    if "." in normalized:
        return normalized
    code = normalized.zfill(6)
    if code.startswith(("6", "5")):
        return f"{code}.SH"
    if code.startswith(("0", "2", "3")):
        return f"{code}.SZ"
    if code.startswith(("4", "8", "9")):
        return f"{code}.BJ"
    return code


def _adjust_to_tickflow(adjust: str) -> str:
    if adjust == "hfq":
        return "backward"
    if adjust == "":
        return "none"
    return "forward"


def _date_to_epoch_millis(value: str, *, end_of_day: bool = False) -> int:
    timestamp = pd.Timestamp(value)
    if end_of_day:
        timestamp = timestamp + pd.Timedelta(days=1) - pd.Timedelta(milliseconds=1)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("Asia/Shanghai")
    return int(timestamp.timestamp() * 1000)


class AbstractDataProvider(ABC):
    @abstractmethod
    def get_ohlcv(self, request: HistoricalDataRequest) -> pd.DataFrame:
        """Fetch OHLCV data."""


class AkshareProvider(AbstractDataProvider):
    """
    Latest AkShare-backed A-share historical data provider.

    The primary upstream is the official AkShare EastMoney history endpoint.
    Lower-priority providers are handled by ``SmartDataProvider`` explicitly so
    the primary/fallback order remains visible and stable.
    """

    source_name = "akshare"

    def _fetch_history(self, symbol: str, start: str, end: str, adjust: str) -> pd.DataFrame:
        return ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start,
            end_date=end,
            adjust=adjust or None,
            timeout=10,
        )

    def get_ohlcv(self, request: HistoricalDataRequest) -> pd.DataFrame:
        start = request.start_date.replace("-", "")
        end = request.end_date.replace("-", "")
        last_error: Exception | None = None
        for retry_index in range(2):
            try:
                raw = self._fetch_history(request.symbol, start, end, request.adjust)
                if raw is None or raw.empty:
                    raise DataProviderError("AkShare 历史行情返回为空")
                return _normalize_columns(raw)
            except Exception as exc:
                last_error = exc
                if retry_index == 1:
                    break
                time.sleep(1 + random.random())

        raise DataProviderError(f"AkShare 历史行情异常: {last_error}")


class SinaDirectProvider(AbstractDataProvider):
    """
    Directly calls Sina Finance API (quotes.sina.cn) similar to go-stock.
    Best for recent data or when AkShare is unstable.
    """
    source_name = "sina_direct"

    def get_ohlcv(self, request: HistoricalDataRequest) -> pd.DataFrame:
        # Sina API uses 'scale=240' for daily K-line
        # It takes 'datalen' (number of points) instead of date range.
        # We estimate datalen based on date range.
        start_dt = pd.to_datetime(request.start_date)
        end_dt = pd.to_datetime(request.end_date)
        today = pd.Timestamp.now()

        # Calculate days from today to start_date to ensure we cover the range
        # Add buffer for weekends/holidays (approx 250 trading days per year)
        # Simple estimation: (Today - Start) * (5/7)
        days_diff = (today - start_dt).days
        datalen = int(days_diff * 0.8) + 100  # Add buffer
        if datalen < 100:
            datalen = 100
        if datalen > 3000:
            datalen = 3000  # Cap to avoid huge requests if API limits

        symbol = request.symbol
        if symbol.startswith("6"):
            code = f"sh{symbol}"
        elif symbol.startswith("0") or symbol.startswith("3"):
            code = f"sz{symbol}"
        elif symbol.startswith("4") or symbol.startswith("8"):
            code = f"bj{symbol}"
        else:
            code = symbol

        url = (
            "http://quotes.sina.cn/cn/api/json_v2.php/"
            f"CN_MarketDataService.getKLineData?symbol={code}&scale=240&ma=no&datalen={datalen}"
        )

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "http://finance.sina.com.cn/",
            }
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()

            if not data:
                raise DataProviderError("Sina API returned empty data")

            df = pd.DataFrame(data)
            df = df.rename(
                columns={
                    "day": "date",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                }
            )

            # Convert columns
            numeric_cols = ["open", "high", "low", "close", "volume"]
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
            df["date"] = pd.to_datetime(df["date"])

            # Filter by date range
            mask = (df["date"] >= start_dt) & (df["date"] <= end_dt)
            df = df.loc[mask]

            if df.empty:
                raise DataProviderError(
                    f"No data found for range {request.start_date} to {request.end_date}"
                )

            df = df.sort_values("date").set_index("date")

            # Sina KLine API 不返回 amount，按均价近似成交额。
            df["amount"] = df["volume"] * (df["open"] + df["close"] + df["high"] + df["low"]) / 4

            # Calculate pre_close
            df["pre_close"] = df["close"].shift(1)
            df["pre_close"] = df["pre_close"].fillna(df["open"])

            return df

        except Exception as e:
            raise DataProviderError(f"Sina Direct API failed: {e}") from e


class TushareProvider(AbstractDataProvider):
    """
    Tushare API Provider.
    Requires `TUSHARE_TOKEN` in the backend `.env` file.
    """
    source_name = "tushare"

    def get_ohlcv(self, request: HistoricalDataRequest) -> pd.DataFrame:
        token = get_backend_env_value("TUSHARE_TOKEN", "")
        if not token:
            raise DataProviderError("Tushare Token not found in backend .env file")

        # Convert symbol to Tushare format (e.g. 600000 -> 600000.SH)
        symbol = request.symbol
        if symbol.startswith("6"):
            ts_code = f"{symbol}.SH"
        elif symbol.startswith("0") or symbol.startswith("3"):
            ts_code = f"{symbol}.SZ"
        elif symbol.startswith("4") or symbol.startswith("8"):
            ts_code = f"{symbol}.BJ"
        else:
            ts_code = symbol  # Try as is

        start_date = request.start_date.replace("-", "")
        end_date = request.end_date.replace("-", "")

        url = "http://api.tushare.pro"
        payload = {
            "api_name": "daily",
            "token": token,
            "params": {
                "ts_code": ts_code,
                "start_date": start_date,
                "end_date": end_date,
            },
            "fields": "trade_date,open,high,low,close,pre_close,vol,amount",
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()

            if data.get("code") != 0:
                raise DataProviderError(f"Tushare API Error: {data.get('msg')}")

            items = data.get("data", {}).get("items", [])
            if not items:
                raise DataProviderError("Tushare returned no data")

            df = pd.DataFrame(
                items,
                columns=[
                    "date",
                    "open",
                    "high",
                    "low",
                    "close",
                    "pre_close",
                    "volume",
                    "amount",
                ],
            )

            # Convert types
            df["date"] = pd.to_datetime(df["date"])
            numeric_cols = ["open", "high", "low", "close", "pre_close", "volume", "amount"]
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

            df = df.sort_values("date").set_index("date")

            # Tushare 的 amount 单位是千元，这里统一换算为元。
            df["amount"] = df["amount"] * 1000

            return df

        except Exception as e:
            raise DataProviderError(f"Tushare request failed: {e}") from e


class TickflowProvider(AbstractDataProvider):
    """
    Optional TickFlow historical day-K provider.

    TickFlow free tier supports historical daily K-lines without an API key.
    Realtime quote fallback is handled by the backend market data service
    because free tier does not provide realtime quotes.
    """

    source_name = "tickflow"

    def __init__(
        self,
        *,
        client_factory=None,
        api_key: str | None = None,
        base_url: str | None = None,
        free_base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.client_factory = client_factory
        resolved_api_key = (
            api_key if api_key is not None else get_backend_env_value("TICKFLOW_API_KEY", "")
        )
        self.api_key = resolved_api_key.strip()
        self.base_url = (
            base_url
            if base_url is not None
            else get_backend_env_value("TICKFLOW_BASE_URL", "https://api.tickflow.org")
        ).strip()
        self.free_base_url = (
            free_base_url
            if free_base_url is not None
            else get_backend_env_value(
                "TICKFLOW_FREE_BASE_URL",
                "https://free-api.tickflow.org",
            )
        ).strip()
        self.timeout = int(timeout or get_backend_env_int("BACKEND_TICKFLOW_TIMEOUT", 10))
        self._client = None

    def _get_client(self):
        if self.client_factory is not None:
            return self.client_factory()
        if self._client is not None:
            return self._client

        try:
            from tickflow import TickFlow
        except Exception as exc:  # pragma: no cover - covered through provider fallback
            raise DataProviderError(f"TickFlow SDK 不可用: {exc}") from exc

        try:
            if self.api_key:
                kwargs = {"api_key": self.api_key, "timeout": self.timeout}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = TickFlow(**kwargs)
            else:
                kwargs = {"timeout": self.timeout}
                if self.free_base_url:
                    kwargs["base_url"] = self.free_base_url
                with redirect_stdout(StringIO()):
                    self._client = TickFlow.free(**kwargs)
        except Exception as exc:
            raise DataProviderError(f"TickFlow 客户端初始化失败: {exc}") from exc

        return self._client

    def get_ohlcv(self, request: HistoricalDataRequest) -> pd.DataFrame:
        symbol = _symbol_to_exchange_suffix(request.symbol)
        try:
            client = self._get_client()
            raw = client.klines.get(
                symbol,
                period="1d",
                count=10000,
                start_time=_date_to_epoch_millis(request.start_date),
                end_time=_date_to_epoch_millis(request.end_date, end_of_day=True),
                adjust=_adjust_to_tickflow(request.adjust),
                as_dataframe=True,
            )
        except Exception as exc:
            raise DataProviderError(f"TickFlow 历史行情异常: {exc}") from exc

        if raw is None or raw.empty:
            raise DataProviderError("TickFlow 历史行情返回为空")

        normalized = _normalize_columns(raw)
        start_dt = pd.Timestamp(request.start_date)
        end_dt = pd.Timestamp(request.end_date)
        filtered = normalized[(normalized.index >= start_dt) & (normalized.index <= end_dt)]
        if filtered.empty:
            raise DataProviderError(
                f"TickFlow 未返回 {request.start_date} 至 {request.end_date} 的历史行情"
            )
        return filtered


class SmartDataProvider(AbstractDataProvider):
    """
    Automatically switches between available data providers.
    Priority: AkShare -> TickFlow -> Tushare -> Sina Direct by default.
    """
    def __init__(self):
        self.providers = []
        self.init_errors = []
        self.last_success_source: str | None = None
        self.last_errors: list[str] = []

        akshare_provider = AkshareProvider()
        tickflow_enabled = _env_flag("BACKEND_MARKET_DATA_ENABLE_TICKFLOW", True)
        tickflow_preferred = _env_flag("BACKEND_MARKET_DATA_PREFER_TICKFLOW", False)
        tickflow_provider = TickflowProvider() if tickflow_enabled else None

        if tickflow_preferred and tickflow_provider is not None:
            self.providers.extend([tickflow_provider, akshare_provider])
        else:
            self.providers.append(akshare_provider)
            if tickflow_provider is not None:
                self.providers.append(tickflow_provider)

        if get_backend_env_value("TUSHARE_TOKEN", ""):
            self.providers.append(TushareProvider())

        self.providers.append(SinaDirectProvider())
        if not tickflow_enabled:
            self.init_errors.append("TickFlow disabled by BACKEND_MARKET_DATA_ENABLE_TICKFLOW")

    def describe_source_order(self) -> list[str]:
        return [
            getattr(provider, "source_name", provider.__class__.__name__.lower())
            for provider in self.providers
        ]

    def describe_sources(self) -> dict[str, object]:
        source_order = self.describe_source_order()
        return {
            "primarySource": source_order[0],
            "fallbackSources": source_order[1:],
            "sourceOrder": source_order,
            "lastSuccessSource": self.last_success_source,
            "providerErrors": list(self.last_errors),
            "skippedProviders": list(self.init_errors),
            "providerCapabilities": {
                "akshare": ["historical_ohlcv", "realtime_quotes", "sectors"],
                "tickflow": ["historical_ohlcv", "quote_fallback_with_api_key"],
                "tushare": ["historical_ohlcv_with_token"],
                "sina_direct": ["last_resort_historical_ohlcv"],
            },
        }

    def get_ohlcv(self, request: HistoricalDataRequest) -> pd.DataFrame:
        errors = []
        self.last_success_source = None
        self.last_errors = []
        for provider in self.providers:
            source_name = getattr(provider, "source_name", provider.__class__.__name__.lower())
            try:
                frame = provider.get_ohlcv(request)
                self.last_success_source = source_name
                self.last_errors = list(errors)
                return frame
            except DataProviderError as e:
                errors.append(f"{source_name}: {e}")
            except Exception as e:
                errors.append(f"{source_name}: {e}")

        all_errors = " | ".join(errors)
        self.last_errors = list(errors)
        if self.init_errors:
            all_errors += f" (Skipped: {'; '.join(self.init_errors)})"

        raise DataProviderError(f"所有数据源均不可用: {all_errors}")
