from __future__ import annotations

from typing import Any

import akshare as ak
import pandas as pd

from .runtime_cache import TTLCache


def _safe_float(value: Any) -> float | None:
    try:
        if value in ("", None, "-"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


class StockDetailService:
    def __init__(self, cache_ttl_seconds: int = 300):
        self._cache: TTLCache[tuple[Any, ...], dict[str, Any]] = TTLCache(cache_ttl_seconds)

    def get_stock_detail(self, symbol: str) -> dict[str, Any]:
        """Get stock fundamentals: company profile, industry, market cap, PE/PB, 52-week high/low, dividend yield."""
        cache_key = ("stock_detail", symbol)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_individual_info_em(symbol=symbol)
            info: dict[str, Any] = {}
            for _, row in df.iterrows():
                key = str(row.get("item") or "").strip()
                val = row.get("value")
                if key:
                    info[key] = val

            # Also get latest quote for 52-week data
            spot_df = ak.stock_zh_a_spot_em()
            spot_row = spot_df[spot_df["代码"] == symbol.zfill(6)]

            result: dict[str, Any] = {
                "symbol": symbol.zfill(6),
                "name": info.get("股票简称", ""),
                "industry": info.get("行业", ""),
                "listedDate": str(info.get("上市时间", "")),
                "totalShares": _safe_float(info.get("总股本")),
                "floatShares": _safe_float(info.get("流通股")),
                "marketCap": _safe_float(info.get("总市值")),
                "floatMarketCap": _safe_float(info.get("流通市值")),
            }

            if not spot_row.empty:
                row = spot_row.iloc[0]
                result.update({
                    "price": _safe_float(row.get("最新价")),
                    "changePercent": _safe_float(row.get("涨跌幅")),
                    "open": _safe_float(row.get("今开")),
                    "high": _safe_float(row.get("最高")),
                    "low": _safe_float(row.get("最低")),
                    "preClose": _safe_float(row.get("昨收")),
                    "volume": _safe_float(row.get("成交量")),
                    "amount": _safe_float(row.get("成交额")),
                    "pe": _safe_float(row.get("市盈率")),
                    "pb": _safe_float(row.get("市净率")),
                    "high52w": _safe_float(row.get("60日最高")),
                    "low52w": _safe_float(row.get("60日最低")),
                    "turnoverRate": _safe_float(row.get("换手率")),
                    "volumeRatio": _safe_float(row.get("量比")),
                })

            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            return {"symbol": symbol, "error": str(e), "degraded": True}

    def get_kline_data(
        self,
        symbol: str,
        period: str = "daily",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get OHLCV data for multiple periods (daily/weekly/monthly/60min/30min/15min/5min)."""
        cache_key = ("kline", symbol, period, start_date, end_date)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            period_map = {
                "daily": "daily",
                "weekly": "weekly",
                "monthly": "monthly",
                "60min": "60",
                "30min": "30",
                "15min": "15",
                "5min": "5",
                "1min": "1",
            }
            ak_period = period_map.get(period, "daily")

            if period in ("daily", "weekly", "monthly"):
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period=ak_period,
                    start_date=start_date or "20240101",
                    end_date=end_date or "",
                    adjust="qfq",
                )
            else:
                df = ak.stock_zh_a_hist_min_em(
                    symbol=symbol,
                    period=ak_period,
                    start_date=start_date or "2024-01-01 09:30:00",
                    end_date=end_date or "",
                    adjust="qfq",
                )

            items: list[dict[str, Any]] = []
            for _, row in df.iterrows():
                item: dict[str, Any] = {
                    "date": str(row.get("日期") or row.get("时间", "")),
                    "open": _safe_float(row.get("开盘")),
                    "high": _safe_float(row.get("最高")),
                    "low": _safe_float(row.get("最低")),
                    "close": _safe_float(row.get("收盘")),
                    "volume": _safe_float(row.get("成交量")),
                    "amount": _safe_float(row.get("成交额")),
                }
                turnover = _safe_float(row.get("换手率"))
                if turnover is not None:
                    item["turnover"] = turnover
                items.append(item)

            result: dict[str, Any] = {
                "symbol": symbol.zfill(6),
                "period": period,
                "items": items,
                "source": "akshare",
                "degraded": False,
            }
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            return {"symbol": symbol, "period": period, "items": [], "error": str(e), "degraded": True}

    def get_financial_summary(self, symbol: str) -> dict[str, Any]:
        """Get financial summary: income statement, balance sheet, cash flow snapshot."""
        cache_key = ("financials", symbol)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_financial_abstract_ths(symbol=symbol)
            items: list[dict[str, Any]] = []
            for _, row in df.head(8).iterrows():
                items.append({
                    "reportDate": str(row.get("报告期", "")),
                    "revenue": _safe_float(row.get("营业总收入")),
                    "netIncome": _safe_float(row.get("净利润")),
                    "totalAssets": _safe_float(row.get("总资产")),
                    "totalLiabilities": _safe_float(row.get("总负债")),
                    "roe": _safe_float(row.get("净资产收益率")),
                    "grossMargin": _safe_float(row.get("毛利率")),
                    "netMargin": _safe_float(row.get("净利率")),
                })
            result: dict[str, Any] = {
                "symbol": symbol.zfill(6),
                "items": items,
                "source": "akshare",
                "degraded": False,
            }
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            return {"symbol": symbol, "items": [], "error": str(e), "degraded": True}

    def get_stock_news(self, symbol: str, limit: int = 10) -> dict[str, Any]:
        """Get recent news specific to a stock."""
        cache_key = ("stock_news", symbol, limit)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_news_em(symbol=symbol)
            items: list[dict[str, Any]] = []
            for _, row in df.head(limit).iterrows():
                items.append({
                    "title": str(row.get("新闻标题", "")),
                    "content": str(row.get("新闻内容", ""))[:200],
                    "publishedAt": str(row.get("发布时间", "")),
                    "source": str(row.get("文章来源", "")),
                    "url": str(row.get("新闻链接", "")),
                })
            result: dict[str, Any] = {
                "symbol": symbol.zfill(6),
                "items": items,
                "source": "akshare",
                "degraded": False,
            }
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            return {"symbol": symbol, "items": [], "error": str(e), "degraded": True}
