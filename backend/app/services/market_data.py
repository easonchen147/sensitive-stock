from __future__ import annotations

from typing import Any

import akshare as ak
import pandas as pd
import requests

from .runtime_cache import TTLCache


def _safe_float(value: Any) -> float | None:
    try:
        if value in ("", None, "-"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


class AkshareMarketDataService:
    def __init__(
        self,
        akshare_client: Any | None = None,
        session: requests.Session | None = None,
        timeout: int = 10,
        cache_ttl_seconds: int = 300,
        retry_attempts: int = 2,
    ) -> None:
        self.akshare_client = akshare_client or ak
        self.session = session or requests.Session()
        self.timeout = timeout
        self.retry_attempts = max(1, retry_attempts)
        self._cache: TTLCache[tuple[Any, ...], dict[str, Any]] = TTLCache(cache_ttl_seconds)

    def get_market_overview(self) -> dict[str, Any]:
        source_details = self._get_source_details()
        return {
            **source_details,
            "routes": {
                "quotes": "/api/v1/market/quotes",
                "sectors": "/api/v1/market/sectors",
                "news": "/api/v1/market/news",
                "newsIntelligence": "/api/v1/market/news/intelligence",
            },
        }

    def get_quotes(self, symbols: list[str]) -> dict[str, Any]:
        normalized_symbols = [symbol.strip() for symbol in symbols if symbol.strip()]
        cache_key = ("quotes", tuple(normalized_symbols))
        try:
            dataframe = self.akshare_client.stock_zh_a_spot_em()
            items = self._normalize_quote_rows(dataframe, normalized_symbols)
            payload = {
                "source": "akshare",
                "degraded": False,
                "warnings": [],
                "items": items,
            }
        except Exception as primary_error:
            try:
                items = self._fetch_quotes_from_eastmoney(normalized_symbols)
                warning = (
                    "主行情报价源暂不可用，已切换备用报价源："
                    f"{_format_error(primary_error)}"
                )
                payload = {
                    "source": "eastmoney_direct",
                    "degraded": True,
                    "warnings": [warning],
                    "items": items,
                }
            except Exception as fallback_error:
                cached = self._cache.get(cache_key)
                if cached is None:
                    return {
                        "source": "unavailable",
                        "degraded": True,
                        "warnings": [
                            "报价刷新失败，暂未获得可用行情数据："
                            f"{_format_error(fallback_error)}"
                        ],
                        "items": [],
                    }
                warning = (
                    "报价刷新失败，已使用缓存行情数据："
                    f"{_format_error(fallback_error)}"
                )
                return self._as_degraded_cache_payload(
                    cached,
                    warning,
                )

        self._cache.set(cache_key, payload)
        return payload

    def get_hot_sectors(self, limit: int = 5, sector_type: str = "concept") -> dict[str, Any]:
        cache_key = ("sectors", sector_type, limit)
        try:
            dataframe = (
                self.akshare_client.stock_board_industry_name_em()
                if sector_type == "industry"
                else self.akshare_client.stock_board_concept_name_em()
            )
            items = self._normalize_sector_rows(dataframe, sector_type, limit)
            payload = {
                "source": "akshare",
                "degraded": False,
                "warnings": [],
                "sectorType": sector_type,
                "items": items[:limit],
            }
        except Exception as primary_error:
            try:
                items = self._fetch_sectors_from_eastmoney(limit=limit, sector_type=sector_type)
                warning = (
                    "主板块数据源暂不可用，已切换备用板块源："
                    f"{_format_error(primary_error)}"
                )
                payload = {
                    "source": "eastmoney_direct",
                    "degraded": True,
                    "warnings": [warning],
                    "sectorType": sector_type,
                    "items": items[:limit],
                }
            except Exception as fallback_error:
                cached = self._cache.get(cache_key)
                if cached is None:
                    return {
                        "source": "unavailable",
                        "degraded": True,
                        "warnings": [
                            "板块刷新失败，暂未获得可用行情数据："
                            f"{_format_error(fallback_error)}"
                        ],
                        "sectorType": sector_type,
                        "items": [],
                    }
                warning = (
                    "板块刷新失败，已使用缓存行情数据："
                    f"{_format_error(fallback_error)}"
                )
                return self._as_degraded_cache_payload(
                    cached,
                    warning,
                )

        self._cache.set(cache_key, payload)
        return payload

    def list_sector_catalog(self) -> list[dict[str, str]]:
        catalog: list[dict[str, str]] = []
        for sector_type, fetcher in (
            ("concept", getattr(self.akshare_client, "stock_board_concept_name_em", None)),
            ("industry", getattr(self.akshare_client, "stock_board_industry_name_em", None)),
        ):
            if fetcher is None:
                continue
            try:
                dataframe = fetcher()
            except Exception:
                continue

            for _, row in dataframe.iterrows():
                name = str(row.get("板块名称") or row.get("名称") or "").strip()
                if name:
                    catalog.append({"name": name, "boardType": sector_type})
        return catalog

    def _get_source_details(self) -> dict[str, Any]:
        from backtesting.data import SmartDataProvider

        return SmartDataProvider().describe_sources()

    def _normalize_quote_rows(
        self,
        dataframe: pd.DataFrame,
        symbols: list[str],
    ) -> list[dict[str, Any]]:
        if dataframe.empty:
            return []

        rename_map = {
            "代码": "symbol",
            "名称": "name",
            "最新价": "price",
            "涨跌幅": "changePercent",
            "涨跌额": "changeAmount",
            "成交量": "volume",
            "成交额": "amount",
            "今开": "open",
            "昨收": "preClose",
            "最高": "high",
            "最低": "low",
        }
        normalized = dataframe.rename(columns=rename_map).copy()
        if "symbol" not in normalized.columns:
            return []

        normalized["symbol"] = normalized["symbol"].astype(str).str.zfill(6)
        if symbols:
            normalized = normalized[normalized["symbol"].isin(symbols)]

        items: list[dict[str, Any]] = []
        for _, row in normalized.iterrows():
            items.append(
                {
                    "symbol": row.get("symbol"),
                    "name": row.get("name"),
                    "price": _safe_float(row.get("price")),
                    "changePercent": _safe_float(row.get("changePercent")),
                    "changeAmount": _safe_float(row.get("changeAmount")),
                    "volume": _safe_float(row.get("volume")),
                    "amount": _safe_float(row.get("amount")),
                    "open": _safe_float(row.get("open")),
                    "preClose": _safe_float(row.get("preClose")),
                    "high": _safe_float(row.get("high")),
                    "low": _safe_float(row.get("low")),
                }
            )
        return items

    def _normalize_sector_rows(
        self,
        dataframe: pd.DataFrame,
        sector_type: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        if dataframe.empty:
            return []

        items: list[dict[str, Any]] = []
        for _, row in dataframe.head(limit).iterrows():
            items.append(
                {
                    "name": row.get("板块名称") or row.get("名称"),
                    "code": row.get("板块代码") or row.get("代码"),
                    "type": sector_type,
                    "changePercent": _safe_float(row.get("涨跌幅")),
                    "leadingStock": row.get("领涨股票"),
                    "leadingStockChangePercent": _safe_float(row.get("领涨股票-涨跌幅")),
                    "source": "akshare",
                }
            )
        return items

    def _fetch_quotes_from_eastmoney(self, symbols: list[str]) -> list[dict[str, Any]]:
        params = {
            "pn": 1,
            "pz": 5000,
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fields": "f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18",
        }
        payload = self._get_json_with_retries(
            "https://push2.eastmoney.com/api/qt/clist/get",
            params=params,
        )
        rows = (payload.get("data") or {}).get("diff") or []

        items: list[dict[str, Any]] = []
        for row in rows:
            symbol = str(row.get("f12") or "").zfill(6)
            if symbols and symbol not in symbols:
                continue
            items.append(
                {
                    "symbol": symbol,
                    "name": row.get("f14"),
                    "price": _safe_float(row.get("f2")),
                    "changePercent": _safe_float(row.get("f3")),
                    "changeAmount": _safe_float(row.get("f4")),
                    "volume": _safe_float(row.get("f5")),
                    "amount": _safe_float(row.get("f6")),
                    "high": _safe_float(row.get("f15")),
                    "low": _safe_float(row.get("f16")),
                    "open": _safe_float(row.get("f17")),
                    "preClose": _safe_float(row.get("f18")),
                }
            )
        return items

    def _fetch_sectors_from_eastmoney(self, limit: int, sector_type: str) -> list[dict[str, Any]]:
        params = {
            "pn": 1,
            "pz": limit,
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:90 t:2" if sector_type == "industry" else "m:90 t:3",
            "fields": "f12,f14,f3,f128,f136",
        }
        payload = self._get_json_with_retries(
            "https://push2.eastmoney.com/api/qt/clist/get",
            params=params,
        )
        rows = (payload.get("data") or {}).get("diff") or []

        items: list[dict[str, Any]] = []
        for row in rows:
            items.append(
                {
                    "name": row.get("f14"),
                    "code": row.get("f12"),
                    "type": sector_type,
                    "changePercent": _safe_float(row.get("f3")),
                    "leadingStock": row.get("f128"),
                    "leadingStockChangePercent": _safe_float(row.get("f136")),
                    "source": "eastmoney_direct",
                }
            )
        return items

    def _get_json_with_retries(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for _ in range(self.retry_attempts):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as error:  # noqa: PERF203
                last_error = error

        raise RuntimeError(f"东方财富请求失败：{_format_error(last_error)}")

    def _as_degraded_cache_payload(self, payload: dict[str, Any], warning: str) -> dict[str, Any]:
        warnings = list(payload.get("warnings") or [])
        warnings.append(warning)
        return {
            **payload,
            "degraded": True,
            "warnings": warnings,
        }


def _format_error(error: Exception | None) -> str:
    if error is None:
        return "未知错误"
    return f"{error.__class__.__name__}: {error}"
