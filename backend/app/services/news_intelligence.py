from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

import requests

from .deepseek_prediction import DeepSeekMarketPredictionService
from .market_data import AkshareMarketDataService
from .runtime_cache import TTLCache

TAG_RE = re.compile(r"<[^>]+>")
CN_TOKEN_RE = re.compile(r"[\u4e00-\u9fa5]{2,6}")
EN_TOKEN_RE = re.compile(r"\b[A-Z]{2,8}\b")
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
        return {
            **latest_payload,
            "keywords": keywords,
            "sectorHints": sector_hints,
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
        prediction_payload = self.prediction_service.predict(
            items=latest_payload["items"],
            keywords=keywords,
            sector_hints=sector_hints,
            symbols=symbols or [],
            thinking_type=thinking_type,
            reasoning_effort=reasoning_effort,
        )
        return {
            **latest_payload,
            "keywords": keywords,
            "sectorHints": sector_hints,
            **prediction_payload,
            "backtestHandoff": self._build_backtest_handoff(symbols or []),
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

    def _build_backtest_handoff(self, symbols: list[str]) -> dict[str, Any]:
        return {
            "endpoint": "/api/v1/backtests/run",
            "suggestedPreset": "event_theme_momentum",
            "symbols": symbols,
            "defaultParams": {
                "lookback_window": 20,
                "volume_window": 5,
                "volume_multiplier": 1.2,
            },
            "notes": [
                "Use this handoff to validate prediction candidates through AKQuant backtests.",
                "Predictions are research hints and should not be treated as trading instructions.",
            ],
        }


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
