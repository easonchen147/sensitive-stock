from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

import requests

from .market_data import AkshareMarketDataService

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
    ) -> None:
        self.session = session or requests.Session()
        self.flash_api_url = flash_api_url
        self.fallback_url = fallback_url
        self.app_id = app_id
        self.api_version = api_version
        self.channel = channel
        self.timeout = timeout

    def get_latest(self, limit: int = 100) -> dict[str, Any]:
        requested_limit = max(1, min(limit, 100))
        try:
            items = self._fetch_latest_from_flash_api(requested_limit)
            return {
                "source": "jin10_flash_api",
                "requestedLimit": requested_limit,
                "degraded": False,
                "items": items,
            }
        except Exception:
            items = self._fetch_latest_from_public_feed(requested_limit)
            return {
                "source": "jin10_flash_newest_js",
                "requestedLimit": requested_limit,
                "degraded": True,
                "items": items,
            }

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


class MarketNewsIntelligenceService:
    def __init__(
        self,
        news_service: Jin10NewsService | None = None,
        market_data_service: AkshareMarketDataService | None = None,
    ) -> None:
        self.news_service = news_service or Jin10NewsService()
        self.market_data_service = market_data_service or AkshareMarketDataService()

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
