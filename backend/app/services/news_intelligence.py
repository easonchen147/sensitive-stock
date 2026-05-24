from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import urljoin

import requests

from .deepseek_prediction import DeepSeekMarketPredictionService
from .market_data import AkshareMarketDataService
from .runtime_cache import TTLCache

TAG_RE = re.compile(r"<[^>]+>")
NEXT_DATA_RE = re.compile(
    r"<script[^>]+id=[\"']__NEXT_DATA__[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
CN_TOKEN_RE = re.compile(r"[\u4e00-\u9fa5]{2,6}")
EN_TOKEN_RE = re.compile(r"\b[A-Z]{2,8}\b")
STCN_ARTICLE_RE = re.compile(r"(?:https?://(?:www\.)?stcn\.com)?/article/detail/\d+\.html$")
JINGJI21_ARTICLE_RE = re.compile(
    r"(?:https?://(?:www\.)?21jingji\.com)?/article/.+?\.html$"
)
STOCK_CODE_RE = re.compile(r"\b\d{6}\b")
SECURITY_NAME_RE = re.compile(r"(?:证券简称|证券名称|股票简称)\s*([A-Za-z\u4e00-\u9fa5]{2,16})")
CHINA_TIMEZONE = timezone(timedelta(hours=8))
STOP_WORDS = {
    "消息",
    "报道",
    "表示",
    "记者",
    "市场",
    "行业",
    "公司",
    "今日",
    "昨日",
    "数据",
    "影响",
}
EVENT_RULES: tuple[dict[str, Any], ...] = (
    {
        "eventType": "share_buyback",
        "label": "股份回购",
        "signal": "bullish",
        "baseScore": 3.8,
        "phrases": ("回购",),
    },
    {
        "eventType": "shareholder_increase",
        "label": "股东增持",
        "signal": "bullish",
        "baseScore": 3.6,
        "phrases": ("增持",),
    },
    {
        "eventType": "equity_incentive",
        "label": "股权激励",
        "signal": "bullish",
        "baseScore": 3.4,
        "phrases": ("股权激励", "限制性股票", "员工持股计划"),
    },
    {
        "eventType": "order_win",
        "label": "中标与订单",
        "signal": "bullish",
        "baseScore": 3.2,
        "phrases": ("中标", "重大合同", "签订合同", "新增订单", "订单"),
    },
    {
        "eventType": "earnings_guidance_positive",
        "label": "业绩预增与扭亏",
        "signal": "bullish",
        "baseScore": 3.4,
        "phrases": ("业绩预增", "扭亏为盈", "同比增长", "业绩快报"),
    },
    {
        "eventType": "dividend_distribution",
        "label": "分红派息",
        "signal": "bullish",
        "baseScore": 3.0,
        "phrases": ("分红", "派息", "利润分配"),
    },
    {
        "eventType": "shareholder_reduction",
        "label": "股东减持",
        "signal": "bearish",
        "baseScore": 3.6,
        "phrases": ("减持",),
    },
    {
        "eventType": "regulatory_inquiry",
        "label": "监管问询",
        "signal": "bearish",
        "baseScore": 4.1,
        "phrases": ("问询函", "关注函", "监管函", "工作函"),
    },
    {
        "eventType": "investigation_penalty",
        "label": "立案与处罚",
        "signal": "bearish",
        "baseScore": 4.2,
        "phrases": ("立案", "行政处罚", "处罚", "警示函"),
    },
    {
        "eventType": "delisting_risk",
        "label": "退市与风险提示",
        "signal": "bearish",
        "baseScore": 4.3,
        "phrases": ("退市风险", "终止上市", "风险提示"),
    },
    {
        "eventType": "shareholder_meeting",
        "label": "股东大会与董事会",
        "signal": "neutral",
        "baseScore": 2.2,
        "phrases": ("股东大会", "董事会", "监事会"),
    },
    {
        "eventType": "trading_halt_resume",
        "label": "停复牌",
        "signal": "neutral",
        "baseScore": 2.5,
        "phrases": ("停牌", "复牌"),
    },
)


class Jin10NewsService:
    def __init__(
        self,
        session: requests.Session | None = None,
        flash_api_url: str = "https://flash-api.jin10.com/get_flash_list",
        fallback_url: str = "https://www.jin10.com/flash_newest.js",
        app_id: str = "bVBF4FyRTn5NJF5n",
        api_version: str = "1.0.0",
        channel: str = "-8200",
        timeout: int = 10,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self.session = session or requests.Session()
        self.flash_api_url = flash_api_url
        self.fallback_url = fallback_url
        self.app_id = app_id
        self.api_version = api_version
        self.channel = channel
        self.timeout = timeout
        self._latest_cache: TTLCache[tuple[str, int], dict[str, Any]] = TTLCache(
            cache_ttl_seconds
        )

    def get_latest(self, limit: int = 100) -> dict[str, Any]:
        requested_limit = max(1, min(limit, 100))
        cache_key = ("latest", requested_limit)
        try:
            items = self._fetch_latest_from_flash_api(requested_limit)
            payload = {
                "source": "jin10_flash_api",
                "requestedLimit": requested_limit,
                "degraded": False,
                "warnings": [],
                "items": items,
            }
        except Exception as primary_error:
            try:
                items = self._fetch_latest_from_public_feed(requested_limit)
                warning = (
                    "金十快讯接口暂不可用，已切换公开快讯源："
                    f"{_format_error(primary_error)}"
                )
                payload = {
                    "source": "jin10_flash_newest_js",
                    "requestedLimit": requested_limit,
                    "degraded": True,
                    "warnings": [warning],
                    "items": items,
                }
            except Exception as fallback_error:
                cached = self._latest_cache.get(cache_key)
                if cached is None:
                    raise
                return self._as_degraded_cache_payload(
                    cached,
                    f"快讯刷新失败，已使用缓存资讯：{_format_error(fallback_error)}",
                )

        self._latest_cache.set(cache_key, payload)
        return payload

    def _fetch_latest_from_flash_api(self, limit: int) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        max_time: str | None = None

        while len(items) < limit:
            page = self._fetch_flash_page(max_time=max_time)
            if not page:
                break

            new_items_added = 0
            for raw_item in page:
                item_id = str(raw_item.get("id") or "").strip()
                if not item_id or item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                items.append(self._normalize_item(raw_item))
                new_items_added += 1
                if len(items) >= limit:
                    break

            next_max_time = str(page[-1].get("time") or "").strip()
            if new_items_added == 0 or not next_max_time or next_max_time == max_time:
                break
            max_time = next_max_time

        if not items:
            raise RuntimeError("jin10 flash api returned no items")
        return items[:limit]

    def _fetch_flash_page(self, max_time: str | None = None) -> list[dict[str, Any]]:
        params = {"channel": self.channel}
        if max_time:
            params["max_time"] = max_time

        response = self.session.get(
            self.flash_api_url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://flash.jin10.com/",
                "x-app-id": self.app_id,
                "x-version": self.api_version,
            },
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != 200:
            raise RuntimeError(f"jin10 flash api error: {payload.get('message')}")
        return payload.get("data") or []

    def _fetch_latest_from_public_feed(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.get(
            self.fallback_url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.jin10.com/",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        if "var newest =" not in response.text:
            raise RuntimeError("jin10 public feed payload invalid")
        json_blob = response.text.split("var newest =", 1)[1].strip().rstrip(";")
        raw_items = json.loads(json_blob)
        return [self._normalize_item(item) for item in raw_items[:limit]]

    def _normalize_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        data = raw_item.get("data") or {}
        content_raw = str(data.get("content") or "").strip()
        title_raw = str(
            data.get("title") or data.get("vip_title") or data.get("name") or ""
        ).strip()
        content = TAG_RE.sub("", content_raw).strip()
        title = TAG_RE.sub("", title_raw).strip()

        if not title:
            title = content[:60] if content else "金十快讯"
        if not content:
            content = self._compose_calendar_content(data) or title

        tags = raw_item.get("tags") or data.get("tags") or []
        normalized_tags = [str(tag).strip() for tag in tags if str(tag).strip()]

        important = bool(raw_item.get("important") == 1 or "<b>" in content_raw.lower())
        return {
            "id": str(raw_item.get("id") or "").strip(),
            "publishedAt": str(raw_item.get("time") or data.get("pub_time") or "").strip(),
            "title": title,
            "content": content,
            "important": important,
            "tags": normalized_tags,
            "sourceUrl": data.get("source_link") or data.get("link") or "",
            "source": "jin10",
        }

    def _compose_calendar_content(self, data: dict[str, Any]) -> str:
        pieces = [
            str(data.get("country") or "").strip(),
            str(data.get("name") or "").strip(),
            f"actual={data.get('actual')}" if data.get("actual") not in (None, "") else "",
            f"previous={data.get('previous')}" if data.get("previous") not in (None, "") else "",
            f"consensus={data.get('consensus')}" if data.get("consensus") not in (None, "") else "",
        ]
        return " ".join(piece for piece in pieces if piece)

    def _as_degraded_cache_payload(self, payload: dict[str, Any], warning: str) -> dict[str, Any]:
        warnings = list(payload.get("warnings") or [])
        warnings.append(warning)
        return {
            **payload,
            "degraded": True,
            "warnings": warnings,
        }


class EastmoneyMarketNewsSource:
    name = "Eastmoney"
    source = "eastmoney_stock_news"

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        url: str = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns",
        timeout: int = 10,
    ) -> None:
        self.session = session or requests.Session()
        self.url = url
        self.timeout = timeout

    def fetch(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.get(
            self.url,
            params={
                "client": "web",
                "biz": "web_news_col",
                "column": "news",
                "order": 1,
                "needInteractData": 0,
                "page_index": 1,
                "page_size": limit,
            },
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        raw_items = _extract_first_list(payload, ["list", "news", "items", "data"])
        return [
            _normalize_external_item(item, source=self.source, prefix="eastmoney")
            for item in raw_items[:limit]
        ]


class SinaFinanceNewsSource:
    name = "Sina Finance"
    source = "sina_finance_live"

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        url: str = "https://zhibo.sina.com.cn/api/zhibo/feed",
        timeout: int = 10,
    ) -> None:
        self.session = session or requests.Session()
        self.url = url
        self.timeout = timeout

    def fetch(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.get(
            self.url,
            params={"page": 1, "page_size": limit, "zhibo_id": 152, "tag_id": 0},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            payload = _parse_jsonp_payload(response.text)
        raw_items = _extract_first_list(payload, ["list", "feed", "items", "data"])
        return [
            _normalize_external_item(item, source=self.source, prefix="sina")
            for item in raw_items[:limit]
        ]


class ClsTelegraphNewsSource:
    name = "CLS Telegraph"
    source = "cls_telegraph"

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        url: str = "https://www.cls.cn/telegraph",
        timeout: int = 10,
    ) -> None:
        self.session = session or requests.Session()
        self.url = url
        self.timeout = timeout

    def fetch(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.get(
            self.url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.cls.cn/",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        raw_items = _extract_cls_telegraph_items(_response_text(response))
        if not raw_items:
            raise RuntimeError("CLS telegraph page returned no structured items")
        return [self._normalize_item(item) for item in raw_items[:limit]]

    def _normalize_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        title = TAG_RE.sub(
            "",
            str(raw_item.get("title") or _extract_bracket_title(raw_item.get("content")) or ""),
        ).strip()
        content = TAG_RE.sub(
            "",
            str(raw_item.get("content") or raw_item.get("brief") or title),
        ).strip()
        tags = raw_item.get("tags") or []
        if isinstance(tags, str):
            normalized_tags = [
                item.strip() for item in re.split(r"[,，\s]+", tags) if item.strip()
            ]
        else:
            normalized_tags = []
            for item in tags:
                if isinstance(item, dict):
                    normalized = str(
                        item.get("name") or item.get("label") or item.get("title") or ""
                    ).strip()
                else:
                    normalized = str(item).strip()
                if normalized:
                    normalized_tags.append(normalized)

        source_url = str(
            raw_item.get("shareurl") or raw_item.get("assocArticleUrl") or ""
        ).strip()
        if source_url:
            source_url = urljoin(self.url, source_url)
        return {
            "id": f"cls:{raw_item.get('id')}",
            "publishedAt": _normalize_china_timestamp(
                raw_item.get("ctime") or raw_item.get("modified_time")
            ),
            "title": title or content[:60] or self.source,
            "content": content or title,
            "important": bool(
                raw_item.get("is_top")
                or raw_item.get("bold")
                or str(raw_item.get("level") or "").strip().upper() in {"A", "B"}
            ),
            "tags": normalized_tags,
            "sourceUrl": source_url,
            "source": self.source,
        }


class StcnArticleListSource:
    name = "STCN"
    source = "stcn_headlines"

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        url: str = "https://www.stcn.com/",
        timeout: int = 10,
    ) -> None:
        self.session = session or requests.Session()
        self.url = url
        self.timeout = timeout

    def fetch(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.get(
            self.url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        items = _extract_headline_items(
            _response_text(response),
            limit=limit,
            base_url=self.url,
            source=self.source,
            prefix="stcn",
            article_pattern=STCN_ARTICLE_RE,
        )
        if not items:
            raise RuntimeError("STCN homepage returned no article headlines")
        return items


class TwentyOneJingjiArticleListSource:
    name = "21st Century Business Herald"
    source = "jingji21_capital_headlines"

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        url: str = "https://www.21jingji.com/channel/capital",
        timeout: int = 10,
    ) -> None:
        self.session = session or requests.Session()
        self.url = url
        self.timeout = timeout

    def fetch(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.get(
            self.url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        items = _extract_headline_items(
            _response_text(response),
            limit=limit,
            base_url=self.url,
            source=self.source,
            prefix="jingji21",
            article_pattern=JINGJI21_ARTICLE_RE,
            published_at_extractor=_extract_21jingji_published_at,
        )
        if not items:
            raise RuntimeError("21jingji capital page returned no article headlines")
        return items


class CninfoDisclosureNewsSource:
    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        url: str = "https://www.cninfo.com.cn/new/disclosure",
        referer_url: str = "https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
        static_base_url: str = "https://static.cninfo.com.cn/",
        column: str,
        market_name: str,
        source: str,
        timeout: int = 10,
    ) -> None:
        self.session = session or requests.Session()
        self.url = url
        self.referer_url = referer_url
        self.static_base_url = static_base_url
        self.column = column
        self.market_name = market_name
        self.source = source
        self.timeout = timeout
        self.name = f"巨潮公告-{market_name}"

    def fetch(self, limit: int) -> list[dict[str, Any]]:
        response = self.session.post(
            self.url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": self.referer_url,
                "X-Requested-With": "XMLHttpRequest",
            },
            data={
                "column": self.column,
                "pageNum": 1,
                "pageSize": max(1, limit),
                "sortName": "",
                "sortType": "",
                "clusterFlag": "false",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        raw_items = _extract_cninfo_announcement_rows(payload)
        if not raw_items:
            raise RuntimeError(f"CNInfo disclosure returned no items for column {self.column}")
        return [self._normalize_item(item) for item in raw_items[:limit]]

    def _normalize_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        title = str(raw_item.get("announcementTitle") or "").strip()
        sec_name = str(raw_item.get("secName") or "").strip()
        sec_code = str(raw_item.get("secCode") or "").strip()
        type_name = str(raw_item.get("announcementTypeName") or "").strip()
        source_url = str(raw_item.get("adjunctUrl") or "").strip()
        if source_url:
            source_url = urljoin(self.static_base_url, source_url)

        tags = [self.market_name, "公告"]
        for item in [type_name, sec_name, sec_code]:
            if item and item not in tags:
                tags.append(item)

        content_parts = [
            f"市场 {self.market_name}",
            f"证券简称 {sec_name}" if sec_name else "",
            f"证券代码 {sec_code}" if sec_code else "",
            f"公告类型 {type_name}" if type_name else "",
            title,
        ]
        content = "；".join(part for part in content_parts if part)
        return {
            "id": f"{self.source}:{raw_item.get('announcementId')}",
            "publishedAt": _normalize_china_timestamp(raw_item.get("announcementTime")),
            "title": title or content[:60] or self.source,
            "content": content or title,
            "important": bool(raw_item.get("important")),
            "tags": tags,
            "sourceUrl": source_url,
            "source": self.source,
        }


class MultiSourceNewsService:
    def __init__(
        self,
        *,
        primary_service: Jin10NewsService | None = None,
        extra_sources: list[Any] | None = None,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self.primary_service = primary_service or Jin10NewsService()
        self.extra_sources = extra_sources or [
            EastmoneyMarketNewsSource(),
            SinaFinanceNewsSource(),
            ClsTelegraphNewsSource(),
            StcnArticleListSource(),
            TwentyOneJingjiArticleListSource(),
            CninfoDisclosureNewsSource(
                column="szse_latest",
                market_name="深市",
                source="cninfo_szse_disclosures",
            ),
            CninfoDisclosureNewsSource(
                column="sse_latest",
                market_name="沪市",
                source="cninfo_sse_disclosures",
            ),
            CninfoDisclosureNewsSource(
                column="bj_latest",
                market_name="北交所",
                source="cninfo_bse_disclosures",
            ),
        ]
        self._latest_cache: TTLCache[tuple[str, int], dict[str, Any]] = TTLCache(
            cache_ttl_seconds
        )

    def get_latest(self, limit: int = 100) -> dict[str, Any]:
        requested_limit = max(1, min(limit, 100))
        cache_key = ("multi_latest", requested_limit)
        warnings: list[str] = []
        channels: list[dict[str, Any]] = []
        items: list[dict[str, Any]] = []

        try:
            primary_payload = self.primary_service.get_latest(limit=requested_limit)
            primary_items = primary_payload.get("items") or []
            items.extend(primary_items)
            primary_warnings = [str(item) for item in primary_payload.get("warnings") or []]
            warnings.extend(primary_warnings)
            channels.append(
                {
                    "name": "Jin10",
                    "source": primary_payload.get("source", "jin10"),
                    "status": "degraded" if primary_payload.get("degraded") else "ok",
                    "itemCount": len(primary_items),
                    "warnings": primary_warnings,
                }
            )
        except Exception as error:
            warning = f"金十渠道失败：{_format_error(error)}"
            warnings.append(warning)
            channels.append(
                {
                    "name": "Jin10",
                    "source": "jin10",
                    "status": "failed",
                    "itemCount": 0,
                    "warnings": [warning],
                }
            )

        for source in self.extra_sources:
            try:
                source_items = source.fetch(requested_limit)
                items.extend(source_items)
                channels.append(
                    {
                        "name": getattr(source, "name", getattr(source, "source", "unknown")),
                        "source": getattr(source, "source", "unknown"),
                        "status": "ok",
                        "itemCount": len(source_items),
                        "warnings": [],
                    }
                )
            except Exception as error:
                warning = (
                    f"{getattr(source, 'name', getattr(source, 'source', 'unknown'))} "
                    f"渠道失败：{_format_error(error)}"
                )
                warnings.append(warning)
                channels.append(
                    {
                        "name": getattr(source, "name", getattr(source, "source", "unknown")),
                        "source": getattr(source, "source", "unknown"),
                        "status": "failed",
                        "itemCount": 0,
                        "warnings": [warning],
                    }
                )

        deduped, dedupe_metadata = _dedupe_news_items(items)
        deduped = deduped[:requested_limit]
        if not deduped:
            cached = self._latest_cache.get(cache_key)
            if cached is None:
                raise RuntimeError("全部市场资讯渠道失败")
            return self._as_degraded_cache_payload(
                cached,
                "全部市场资讯渠道失败，已使用缓存聚合资讯",
            )

        payload = {
            "source": "multi_source_news",
            "primarySource": "jin10",
            "fallbackSources": [
                "jin10_flash_newest_js",
                *[getattr(source, "source", "unknown") for source in self.extra_sources],
            ],
            "requestedLimit": requested_limit,
            "degraded": bool(warnings),
            "warnings": warnings,
            "channels": channels,
            "sourceCount": sum(1 for channel in channels if channel["status"] != "failed"),
            "sourceQuality": _build_source_quality(channels, items, deduped, dedupe_metadata),
            "dedupeMetadata": dedupe_metadata,
            "items": deduped,
        }
        self._latest_cache.set(cache_key, payload)
        return payload

    def _as_degraded_cache_payload(self, payload: dict[str, Any], warning: str) -> dict[str, Any]:
        warnings = list(payload.get("warnings") or [])
        warnings.append(warning)
        return {
            **payload,
            "degraded": True,
            "warnings": warnings,
        }


class MarketNewsIntelligenceService:
    def __init__(
        self,
        news_service: Any | None = None,
        market_data_service: AkshareMarketDataService | None = None,
        prediction_service: DeepSeekMarketPredictionService | None = None,
    ) -> None:
        self.news_service = news_service or Jin10NewsService()
        self.market_data_service = market_data_service or AkshareMarketDataService()
        self.prediction_service = prediction_service or DeepSeekMarketPredictionService()

    def get_latest(self, limit: int = 100) -> dict[str, Any]:
        return self.news_service.get_latest(limit=limit)

    def build_intelligence(self, limit: int = 100) -> dict[str, Any]:
        latest_payload = self.news_service.get_latest(limit=limit)
        keywords = self._extract_keywords(latest_payload["items"])
        sector_hints = self._build_sector_hints(keywords)
        event_hints = self._extract_event_hints(latest_payload["items"])
        return {
            **latest_payload,
            "keywords": keywords,
            "sectorHints": sector_hints,
            "eventHints": event_hints,
        }

    def build_predictions(
        self,
        limit: int = 100,
        symbols: list[str] | None = None,
        thinking_type: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict[str, Any]:
        latest_payload = self.news_service.get_latest(limit=limit)
        keywords = self._extract_keywords(latest_payload["items"])
        sector_hints = self._build_sector_hints(keywords)
        event_hints = self._extract_event_hints(latest_payload["items"])
        prediction_payload = self.prediction_service.predict(
            items=latest_payload["items"],
            keywords=keywords,
            sector_hints=sector_hints,
            event_hints=event_hints,
            symbols=symbols or [],
            thinking_type=thinking_type,
            reasoning_effort=reasoning_effort,
        )
        return {
            **latest_payload,
            "keywords": keywords,
            "sectorHints": sector_hints,
            "eventHints": event_hints,
            **prediction_payload,
            "backtestHandoff": self._build_backtest_handoff(symbols or [], event_hints),
        }

    def _extract_keywords(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        counter: Counter[str] = Counter()
        coverage: Counter[str] = Counter()

        for item in items:
            seen_in_item: set[str] = set()
            for tag in item.get("tags") or []:
                normalized = str(tag).strip()
                if normalized:
                    counter[normalized] += 1
                    seen_in_item.add(normalized)

            text = f"{item.get('title', '')} {item.get('content', '')}"
            candidates = CN_TOKEN_RE.findall(text) + EN_TOKEN_RE.findall(text)
            for token in candidates:
                normalized = token.strip()
                if not normalized or normalized in STOP_WORDS:
                    continue
                counter[normalized] += 1
                seen_in_item.add(normalized)

            for token in seen_in_item:
                coverage[token] += 1

        ranked = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
        return [
            {
                "keyword": keyword,
                "count": count,
                "coverage": coverage.get(keyword, 0),
            }
            for keyword, count in ranked[:30]
        ]

    def _build_sector_hints(self, keywords: list[dict[str, Any]]) -> list[dict[str, Any]]:
        keyword_map = {item["keyword"]: item["count"] for item in keywords}
        sector_catalog = self.market_data_service.list_sector_catalog()

        hints: list[dict[str, Any]] = []
        for sector in sector_catalog:
            matched_keywords = [
                keyword
                for keyword in keyword_map
                if keyword in sector["name"] or sector["name"] in keyword
            ]
            if not matched_keywords:
                continue

            score = sum(keyword_map[keyword] for keyword in matched_keywords)
            hints.append(
                {
                    "name": sector["name"],
                    "boardType": sector["boardType"],
                    "score": score,
                    "matchedKeywords": matched_keywords,
                }
            )

        hints.sort(key=lambda item: (-item["score"], item["name"]))
        return hints[:10]

    def _extract_event_hints(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        aggregates: dict[str, dict[str, Any]] = {}

        for item in items:
            text_parts = [
                str(item.get("title") or ""),
                str(item.get("content") or ""),
                " ".join(str(tag).strip() for tag in item.get("tags") or [] if str(tag).strip()),
            ]
            combined_text = " ".join(part for part in text_parts if part).strip()
            if not combined_text:
                continue

            related_symbols = self._extract_related_symbols(item)
            related_names = self._extract_related_names(item)
            item_score_boost = 0.0
            if item.get("important"):
                item_score_boost += 0.8
            if str(item.get("source") or "").startswith("cninfo_"):
                item_score_boost += 0.9
            if related_symbols:
                item_score_boost += min(0.8, len(related_symbols) * 0.3)

            for rule in EVENT_RULES:
                matched_phrases = [
                    phrase for phrase in rule["phrases"] if phrase and phrase in combined_text
                ]
                if not matched_phrases:
                    continue

                aggregate = aggregates.setdefault(
                    str(rule["eventType"]),
                    {
                        "eventType": rule["eventType"],
                        "label": rule["label"],
                        "signal": rule["signal"],
                        "score": 0.0,
                        "count": 0,
                        "relatedSymbols": [],
                        "relatedNames": [],
                        "sourceIds": [],
                        "matchedTitles": [],
                    },
                )
                aggregate["score"] += float(rule["baseScore"]) + item_score_boost
                aggregate["count"] += 1
                aggregate["relatedSymbols"] = _merge_unique_strings(
                    aggregate["relatedSymbols"],
                    related_symbols,
                )
                aggregate["relatedNames"] = _merge_unique_strings(
                    aggregate["relatedNames"],
                    related_names,
                )
                aggregate["sourceIds"] = _merge_unique_strings(
                    aggregate["sourceIds"],
                    [str(item.get("id") or "").strip()],
                )
                aggregate["matchedTitles"] = _merge_unique_strings(
                    aggregate["matchedTitles"],
                    [str(item.get("title") or "").strip()],
                )

        hints = [
            {
                **value,
                "score": round(min(10.0, float(value["score"])), 2),
                "sourceIds": value["sourceIds"][:8],
                "matchedTitles": value["matchedTitles"][:5],
            }
            for value in aggregates.values()
        ]
        hints.sort(key=lambda item: (-float(item["score"]), -int(item["count"]), item["label"]))
        return hints[:8]

    def _extract_related_symbols(self, item: dict[str, Any]) -> list[str]:
        candidates: list[str] = []
        for value in [item.get("title"), item.get("content"), *(item.get("tags") or [])]:
            candidates.extend(STOCK_CODE_RE.findall(str(value or "")))
        return sorted({code for code in candidates if code})

    def _extract_related_names(self, item: dict[str, Any]) -> list[str]:
        text = f"{item.get('title', '')} {item.get('content', '')}"
        names = [
            match.group(1).strip("；;，,.。 ")
            for match in SECURITY_NAME_RE.finditer(text)
            if match.group(1).strip("；;，,.。 ")
        ]
        return _merge_unique_strings([], names)

    def _build_backtest_handoff(
        self,
        symbols: list[str],
        event_hints: list[dict[str, Any]],
    ) -> dict[str, Any]:
        suggested_symbols = symbols or self._suggest_symbols_from_event_hints(event_hints)
        notes = [
            "可将这里的候选标的直接交给量化回测，用事件主题动量策略做二次验证。",
            "预测结果只用于研究判断与复盘，不应被视为直接交易指令。",
        ]
        if symbols:
            notes.insert(0, "回测交接优先使用用户输入的观察标的。")
        elif suggested_symbols:
            notes.insert(0, "未提供观察标的，已根据高优先级事件提示自动补全候选股票代码。")
        else:
            notes.insert(0, "当前未识别到可自动回填的明确股票代码。")

        return {
            "endpoint": "/api/v1/backtests/run",
            "suggestedPreset": "event_theme_momentum",
            "symbols": suggested_symbols,
            "defaultParams": {
                "lookback_window": 20,
                "volume_window": 5,
                "volume_multiplier": 1.2,
            },
            "notes": notes,
        }

    def _suggest_symbols_from_event_hints(
        self,
        event_hints: list[dict[str, Any]],
        limit: int = 6,
    ) -> list[str]:
        ranked_hints = [
            hint
            for hint in event_hints
            if hint.get("relatedSymbols")
            and (float(hint.get("score") or 0.0) >= 3.5 or int(hint.get("count") or 0) >= 2)
        ]
        if not ranked_hints:
            ranked_hints = [hint for hint in event_hints if hint.get("relatedSymbols")]

        symbols: list[str] = []
        for hint in ranked_hints:
            symbols = _merge_unique_strings(symbols, hint.get("relatedSymbols") or [])
            if len(symbols) >= limit:
                break
        return symbols[:limit]


def _format_error(error: Exception | None) -> str:
    if error is None:
        return "未知错误"
    return f"{error.__class__.__name__}: {error}"


def _extract_first_list(value: Any, candidate_keys: list[str]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []

    for key in candidate_keys:
        nested = value.get(key)
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
        nested_result = _extract_first_list(nested, candidate_keys)
        if nested_result:
            return nested_result

    for nested in value.values():
        nested_result = _extract_first_list(nested, candidate_keys)
        if nested_result:
            return nested_result
    return []


def _parse_jsonp_payload(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if "(" in stripped and stripped.endswith(")"):
        stripped = stripped[stripped.find("(") + 1 : -1]
    return json.loads(stripped)


class _AnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._current_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = next((value for key, value in attrs if key.lower() == "href" and value), None)
        self._current_href = href
        self._current_chunks = []

    def handle_data(self, data: str) -> None:
        if self._current_href is None:
            return
        self._current_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        self.anchors.append((self._current_href, "".join(self._current_chunks)))
        self._current_href = None
        self._current_chunks = []


def _response_text(response: Any) -> str:
    apparent_encoding = str(getattr(response, "apparent_encoding", "") or "").strip()
    if apparent_encoding and hasattr(response, "encoding"):
        response.encoding = apparent_encoding

    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text

    content = getattr(response, "content", b"")
    if isinstance(content, (bytes, bytearray)):
        encoding = apparent_encoding or str(getattr(response, "encoding", "") or "utf-8")
        return bytes(content).decode(encoding, errors="ignore")
    return str(text or "")


def _extract_cls_telegraph_items(html_text: str) -> list[dict[str, Any]]:
    match = NEXT_DATA_RE.search(html_text)
    if match is None:
        raise RuntimeError("CLS telegraph page missing __NEXT_DATA__ payload")
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise RuntimeError("CLS telegraph __NEXT_DATA__ payload is invalid") from error
    return _extract_first_list(payload, ["telegraphList"])


def _extract_cninfo_announcement_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    announcements = payload.get("announcements")
    if isinstance(announcements, list):
        return [item for item in announcements if isinstance(item, dict)]

    classified = payload.get("classifiedAnnouncements")
    if not isinstance(classified, list):
        return []

    rows: list[dict[str, Any]] = []
    for group in classified:
        if isinstance(group, list):
            rows.extend(item for item in group if isinstance(item, dict))
    return rows


def _extract_headline_items(
    html_text: str,
    *,
    limit: int,
    base_url: str,
    source: str,
    prefix: str,
    article_pattern: re.Pattern[str],
    published_at_extractor: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    parser = _AnchorCollector()
    parser.feed(html_text)

    seen_urls: set[str] = set()
    items: list[dict[str, Any]] = []
    for href, raw_text in parser.anchors:
        absolute_url = urljoin(base_url, href)
        if not (
            article_pattern.search(href.strip()) or article_pattern.search(absolute_url.strip())
        ):
            continue
        title = _normalize_anchor_title(raw_text)
        if not title or absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)
        published_at = (
            str(published_at_extractor(absolute_url)).strip()
            if callable(published_at_extractor)
            else ""
        )
        items.append(
            {
                "id": f"{prefix}:{absolute_url}",
                "publishedAt": published_at,
                "title": title,
                "content": title,
                "important": False,
                "tags": [],
                "sourceUrl": absolute_url,
                "source": source,
            }
        )
        if len(items) >= limit:
            break
    return items


def _normalize_anchor_title(raw_text: str) -> str:
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in str(raw_text or "").splitlines()
        if re.sub(r"\s+", " ", line).strip()
    ]
    if lines:
        return lines[0]
    return re.sub(r"\s+", " ", str(raw_text or "")).strip()


def _normalize_china_timestamp(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)) or str(value).strip().isdigit():
        timestamp = float(value)
        if timestamp > 1_000_000_000_000:
            timestamp /= 1000
        return datetime.fromtimestamp(timestamp, tz=CHINA_TIMEZONE).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    return str(value).strip()


def _extract_bracket_title(value: Any) -> str:
    match = re.search(r"[【\[]([^】\]]+)[】\]]", str(value or ""))
    if match is None:
        return ""
    return match.group(1).strip()


def _extract_21jingji_published_at(source_url: str) -> str:
    match = re.search(r"/article/(\d{4})(\d{2})(\d{2})/", source_url)
    if match is None:
        return ""
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"


def _normalize_external_item(
    raw_item: dict[str, Any],
    *,
    source: str,
    prefix: str,
) -> dict[str, Any]:
    title = TAG_RE.sub(
        "",
        str(
            raw_item.get("title")
            or raw_item.get("Title")
            or raw_item.get("name")
            or raw_item.get("content")
            or ""
        ),
    ).strip()
    content = TAG_RE.sub(
        "",
        str(
            raw_item.get("summary")
            or raw_item.get("digest")
            or raw_item.get("content")
            or raw_item.get("Content")
            or title
        ),
    ).strip()
    item_id = str(
        raw_item.get("id")
        or raw_item.get("code")
        or raw_item.get("newsId")
        or raw_item.get("url")
        or f"{prefix}:{title[:40]}"
    ).strip()
    published_at = str(
        raw_item.get("showTime")
        or raw_item.get("time")
        or raw_item.get("ctime")
        or raw_item.get("date")
        or ""
    ).strip()
    tags = raw_item.get("tags") or raw_item.get("keywords") or []
    if isinstance(tags, str):
        normalized_tags = [item.strip() for item in re.split(r"[,，\s]+", tags) if item.strip()]
    else:
        normalized_tags = [str(item).strip() for item in tags if str(item).strip()]
    return {
        "id": f"{prefix}:{item_id}",
        "publishedAt": published_at,
        "title": title or content[:60] or source,
        "content": content or title,
        "important": bool(raw_item.get("important") or raw_item.get("isImportant")),
        "tags": normalized_tags,
        "sourceUrl": raw_item.get("url") or raw_item.get("sourceUrl") or raw_item.get("link") or "",
        "source": source,
    }


def _build_source_quality(
    channels: list[dict[str, Any]],
    original_items: list[dict[str, Any]],
    unique_items: list[dict[str, Any]],
    dedupe_metadata: dict[str, Any],
) -> dict[str, Any]:
    queried_channels = len(channels)
    succeeded_channels = sum(1 for channel in channels if channel["status"] == "ok")
    degraded_channels = sum(1 for channel in channels if channel["status"] == "degraded")
    failed_channels = sum(1 for channel in channels if channel["status"] == "failed")
    total_items = len(original_items)
    unique_items_count = len(unique_items)
    duplicate_items = int(dedupe_metadata["duplicateCount"])
    source_coverage = sorted(
        {
            str(item.get("source") or "unknown")
            for item in unique_items
            if str(item.get("source") or "").strip()
        }
    )
    score_payload = _score_source_quality(
        queried_channels=queried_channels,
        succeeded_channels=succeeded_channels,
        degraded_channels=degraded_channels,
        failed_channels=failed_channels,
        total_items=total_items,
        unique_items=unique_items_count,
        duplicate_items=duplicate_items,
    )
    return {
        "queriedChannels": len(channels),
        "succeededChannels": succeeded_channels,
        "degradedChannels": degraded_channels,
        "failedChannels": failed_channels,
        "totalItems": total_items,
        "uniqueItems": unique_items_count,
        "duplicateItems": duplicate_items,
        "sourceCoverage": source_coverage,
        **score_payload,
    }


def _score_source_quality(
    *,
    queried_channels: int,
    succeeded_channels: int,
    degraded_channels: int,
    failed_channels: int,
    total_items: int,
    unique_items: int,
    duplicate_items: int,
) -> dict[str, Any]:
    if queried_channels <= 0:
        return {
            "qualityScore": 0,
            "coverageScore": 0,
            "freshnessScore": 0,
            "reliabilityScore": 0,
            "duplicatePressure": 0,
            "qualityNotes": ["没有可用资讯渠道。"],
        }

    coverage_score = round(min(100.0, (unique_items / max(total_items, 1)) * 100), 2)
    reliability_score = round(
        max(
            0.0,
            ((succeeded_channels + degraded_channels * 0.5) / queried_channels) * 100,
        ),
        2,
    )
    freshness_score = round(min(100.0, (unique_items / 20) * 100), 2)
    duplicate_pressure = round((duplicate_items / max(total_items, 1)) * 100, 2)
    quality_score = round(
        max(
            0.0,
            min(
                100.0,
                reliability_score * 0.45
                + coverage_score * 0.3
                + freshness_score * 0.2
                - duplicate_pressure * 0.15,
            ),
        ),
        2,
    )
    notes = [
        (
            f"已查询 {queried_channels} 个资讯渠道，成功 {succeeded_channels} 个，"
            f"失败 {failed_channels} 个。"
        ),
        f"合并前 {total_items} 条，去重后 {unique_items} 条，重复压力 {duplicate_pressure:.2f}%。",
    ]
    if failed_channels:
        notes.append("存在失败渠道，预测置信度需要下调参考。")
    if duplicate_pressure > 30:
        notes.append("重复资讯较多，热点可能被单一事件放大。")

    return {
        "qualityScore": quality_score,
        "coverageScore": coverage_score,
        "freshnessScore": freshness_score,
        "reliabilityScore": reliability_score,
        "duplicatePressure": duplicate_pressure,
        "qualityNotes": notes,
    }


def _dedupe_news_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        title = re.sub(r"\s+", "", str(item.get("title") or "")).lower()
        content = re.sub(r"\s+", "", str(item.get("content") or "")).lower()
        source_url = str(item.get("sourceUrl") or "").strip().lower()
        key = source_url or f"{title}:{content[:80]}"
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    deduped.sort(key=lambda item: str(item.get("publishedAt") or ""), reverse=True)
    return deduped, {
        "strategy": "source-url-or-normalized-title-content",
        "originalCount": len(items),
        "uniqueCount": len(deduped),
        "duplicateCount": max(0, len(items) - len(deduped)),
    }


def _merge_unique_strings(existing: list[str], incoming: list[str]) -> list[str]:
    merged = list(existing)
    seen = {str(item).strip() for item in merged if str(item).strip()}
    for item in incoming:
        normalized = str(item).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        merged.append(normalized)
    return merged
