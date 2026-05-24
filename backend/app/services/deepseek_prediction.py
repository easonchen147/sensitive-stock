from __future__ import annotations

import hashlib
import json
from time import perf_counter
from typing import Any

import requests

from .runtime_cache import TTLCache

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_THINKING_TYPE = "enabled"
DEFAULT_REASONING_EFFORT = "high"
PREDICTION_SCHEMA_VERSION = "market-prediction-json-v1"
PREDICTION_SYSTEM_PROMPT = f"""你是谨慎的 A 股市场研究助手。
只返回严格 JSON，不给出交易指令或收益保证。
所有 summary、riskNotes、horizon、drivers 等可读文本都必须使用简体中文。
优先参考 eventHints 里的结构化事件信号，再结合关键词和板块提示补足判断。
使用结构版本：{PREDICTION_SCHEMA_VERSION}。

示例 JSON 输出：
{{
  "summary": "一句简洁的市场研究摘要。",
  "riskNotes": [
    "预测只作为研究上下文，不构成投资建议。",
    "候选方向需要结合回测与更宽市场数据验证。"
  ],
  "predictions": [
    {{
      "targetType": "sector",
      "target": "算力基础设施",
      "direction": "bullish",
      "confidence": 0.65,
      "score": 8.5,
      "horizon": "1 至 3 个交易日",
      "drivers": ["人工智能", "液冷需求"],
      "sourceIds": ["news-1"]
    }}
  ]
}}"""


class DeepSeekMarketPredictionService:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
        model: str = DEFAULT_DEEPSEEK_MODEL,
        thinking_type: str = DEFAULT_THINKING_TYPE,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        session: requests.Session | None = None,
        timeout: int = 10,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.thinking_type = _normalize_thinking_type(thinking_type)
        self.reasoning_effort = _normalize_reasoning_effort(reasoning_effort)
        self.session = session or requests.Session()
        self.timeout = timeout
        self._prediction_cache: TTLCache[str, dict[str, Any]] = TTLCache(
            cache_ttl_seconds
        )

    def predict(
        self,
        *,
        items: list[dict[str, Any]],
        keywords: list[dict[str, Any]],
        sector_hints: list[dict[str, Any]],
        event_hints: list[dict[str, Any]] | None = None,
        symbols: list[str] | None = None,
        thinking_type: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict[str, Any]:
        request_mode = {
            "thinkingType": _normalize_thinking_type(thinking_type or self.thinking_type),
            "reasoningEffort": _normalize_reasoning_effort(
                reasoning_effort or self.reasoning_effort
            ),
        }
        context = {
            "items": items[:30],
            "keywords": keywords[:20],
            "sectorHints": sector_hints[:12],
            "eventHints": (event_hints or [])[:8],
            "symbols": list(symbols or []),
        }
        metadata_base = self._build_metadata_base(context, request_mode)
        cache_key = self._build_cache_key(
            context,
            metadata_base["inputDigest"],
            request_mode,
        )

        if not self.api_key:
            return self._heuristic_prediction(
                context=context,
                metadata_base=metadata_base,
                cache_key=cache_key,
                warnings=["未配置 DeepSeek 访问密钥，已切换为本地启发式预测。"],
            )

        cached_payload = self._prediction_cache.get(cache_key)
        if cached_payload is not None:
            cached_metadata = {
                **cached_payload["predictionMetadata"],
                "cached": True,
                "latencyMs": 0,
            }
            return {
                **cached_payload,
                "predictionMetadata": cached_metadata,
            }

        try:
            started_at = perf_counter()
            request_payload: dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": PREDICTION_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(context, ensure_ascii=False),
                    },
                ],
                "temperature": 0.2,
                "max_tokens": 1200,
                "response_format": {"type": "json_object"},
                "thinking": {"type": request_mode["thinkingType"]},
            }
            if request_mode["thinkingType"] == "enabled":
                request_payload["reasoning_effort"] = request_mode["reasoningEffort"]

            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=request_payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            content = (
                (payload.get("choices") or [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            parsed = json.loads(content)
            predictions = self._normalize_predictions(parsed.get("predictions") or [])
            if not predictions:
                raise ValueError("DeepSeek response contained no usable predictions")
            payload = {
                "predictionMetadata": {
                    "provider": "deepseek",
                    "model": self.model,
                    "requestMode": "remote",
                    "degraded": False,
                    "cached": False,
                    "cacheKey": cache_key,
                    **metadata_base,
                    "latencyMs": round((perf_counter() - started_at) * 1000),
                    "warnings": [],
                },
                "predictions": predictions,
                "predictionSummary": str(parsed.get("summary") or "").strip(),
                "riskNotes": self._normalize_risk_notes(parsed.get("riskNotes")),
            }
            self._prediction_cache.set(cache_key, payload)
            return payload
        except Exception as error:
            return self._heuristic_prediction(
                context=context,
                metadata_base=metadata_base,
                cache_key=cache_key,
                warnings=[
                    "DeepSeek 预测失败，已切换为本地启发式预测："
                    f"{_format_error(error)}"
                ],
            )

    def _heuristic_prediction(
        self,
        *,
        context: dict[str, Any],
        metadata_base: dict[str, Any],
        cache_key: str,
        warnings: list[str],
    ) -> dict[str, Any]:
        predictions: list[dict[str, Any]] = []
        source_ids = [
            str(item.get("id") or "")
            for item in context["items"][:5]
            if str(item.get("id") or "").strip()
        ]

        for hint in context["eventHints"][:4]:
            signal = _normalize_direction(hint.get("signal"))
            score = float(hint.get("score") or 0.0)
            related_symbols = _string_list(hint.get("relatedSymbols"))
            related_names = _string_list(hint.get("relatedNames"))
            target = str(hint.get("label") or "事件提示")
            if related_symbols:
                primary_symbol = related_symbols[0]
                primary_name = related_names[0] if related_names else ""
                target = " ".join(part for part in [primary_symbol, primary_name] if part)
            confidence = max(0.3, min(0.88, 0.38 + score / 12))
            drivers = _string_list(hint.get("matchedTitles"))[:2] or [
                str(hint.get("label") or "事件驱动")
            ]
            predictions.append(
                {
                    "targetType": "symbol" if related_symbols else "event",
                    "target": target,
                    "direction": signal,
                    "confidence": round(confidence, 2),
                    "score": score,
                    "horizon": "1 至 3 个交易日",
                    "drivers": drivers[:5],
                    "sourceIds": _string_list(hint.get("sourceIds"))[:5] or source_ids,
                }
            )

        for hint in context["sectorHints"][:5]:
            score = float(hint.get("score") or 0.0)
            confidence = max(0.25, min(0.78, 0.35 + score / 20))
            matched = [str(item) for item in hint.get("matchedKeywords") or [] if str(item)]
            predictions.append(
                {
                    "targetType": "sector",
                    "target": str(hint.get("name") or "未知目标"),
                    "direction": "bullish" if score >= 2 else "neutral",
                    "confidence": round(confidence, 2),
                    "score": score,
                    "horizon": "1 至 3 个交易日",
                    "drivers": matched[:5] or ["板块关键词命中"],
                    "sourceIds": source_ids,
                }
            )

        if not predictions:
            for keyword in context["keywords"][:5]:
                count = float(keyword.get("count") or 0.0)
                predictions.append(
                    {
                        "targetType": "theme",
                        "target": str(keyword.get("keyword") or "未知主题"),
                        "direction": "neutral",
                        "confidence": round(max(0.2, min(0.6, 0.25 + count / 30)), 2),
                        "score": count,
                        "horizon": "1 至 3 个交易日",
                        "drivers": [str(keyword.get("keyword") or "关键词频次")],
                        "sourceIds": source_ids,
                    }
                )

        if not predictions:
            predictions.append(
                {
                    "targetType": "market",
                    "target": "A 股宽基市场",
                    "direction": "neutral",
                    "confidence": 0.2,
                    "score": 0.0,
                    "horizon": "1 至 3 个交易日",
                    "drivers": ["市场资讯上下文不足"],
                    "sourceIds": source_ids,
                }
            )

        return {
            "predictionMetadata": {
                "provider": "local_heuristic",
                "model": "event-keyword-sector-rules",
                "requestMode": "heuristic",
                "degraded": True,
                "cached": False,
                "cacheKey": cache_key,
                **metadata_base,
                "warnings": warnings,
            },
            "predictions": predictions[:8],
            "predictionSummary": (
                "本地启发式预测优先使用结构化事件提示，再结合关键词频次和板块提示生成。"
            ),
            "riskNotes": self._default_risk_notes(),
        }

    def _normalize_predictions(self, rows: list[Any]) -> list[dict[str, Any]]:
        predictions: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            target = str(row.get("target") or row.get("label") or "").strip()
            if not target:
                continue
            predictions.append(
                {
                    "targetType": str(row.get("targetType") or row.get("type") or "theme"),
                    "target": target,
                    "direction": _normalize_direction(row.get("direction")),
                    "confidence": _bounded_float(row.get("confidence"), default=0.35),
                    "score": _bounded_float(row.get("score"), default=0.0, upper=100.0),
                    "horizon": str(row.get("horizon") or "1 至 3 个交易日"),
                    "drivers": _string_list(row.get("drivers")),
                    "sourceIds": _string_list(row.get("sourceIds")),
                }
            )
        return predictions[:8]

    def _normalize_risk_notes(self, value: Any) -> list[str]:
        notes = _string_list(value)
        return notes or self._default_risk_notes()

    def _build_metadata_base(
        self,
        context: dict[str, Any],
        request_mode: dict[str, str],
    ) -> dict[str, Any]:
        return {
            "schemaVersion": PREDICTION_SCHEMA_VERSION,
            "inputDigest": _digest_payload(context),
            **request_mode,
            "newsItemCount": len(context["items"]),
            "keywordCount": len(context["keywords"]),
            "sectorHintCount": len(context["sectorHints"]),
            "eventHintCount": len(context["eventHints"]),
            "symbolCount": len(context["symbols"]),
        }

    def _build_cache_key(
        self,
        context: dict[str, Any],
        input_digest: str,
        request_mode: dict[str, str],
    ) -> str:
        cache_payload = {
            "model": self.model,
            "schemaVersion": PREDICTION_SCHEMA_VERSION,
            "inputDigest": input_digest,
            **request_mode,
            "symbols": context["symbols"],
        }
        return _digest_payload(cache_payload)

    def _default_risk_notes(self) -> list[str]:
        return [
            "预测只作为研究上下文，不构成投资建议。",
            "候选标的需要结合回测和更宽市场数据验证。",
            "外部资讯和模型输出可能不完整、延迟或错误。",
        ]


def _normalize_direction(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"bullish", "bearish", "neutral"}:
        return normalized
    if normalized in {"up", "positive", "long"}:
        return "bullish"
    if normalized in {"down", "negative", "short"}:
        return "bearish"
    return "neutral"


def _normalize_thinking_type(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"enabled", "disabled"}:
        return normalized
    return DEFAULT_THINKING_TYPE


def _normalize_reasoning_effort(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"high", "max"}:
        return normalized
    return DEFAULT_REASONING_EFFORT


def _bounded_float(value: Any, *, default: float, upper: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return round(max(0.0, min(upper, number)), 4)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _digest_payload(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()[:16]


def _format_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {error}"
