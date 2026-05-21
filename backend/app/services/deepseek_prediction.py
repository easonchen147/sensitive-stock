from __future__ import annotations

import hashlib
import json
from time import perf_counter
from typing import Any

import requests

from .runtime_cache import TTLCache

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
PREDICTION_SCHEMA_VERSION = "market-prediction-json-v1"
PREDICTION_SYSTEM_PROMPT = f"""You are a cautious A-share market research assistant.
Return strict JSON only. Never provide trading instructions or guarantees.
Use this schema version: {PREDICTION_SCHEMA_VERSION}.

EXAMPLE JSON OUTPUT:
{{
  "summary": "One concise market-research summary.",
  "riskNotes": [
    "Predictions are research context, not investment advice.",
    "Validate candidates with AKQuant backtests."
  ],
  "predictions": [
    {{
      "targetType": "sector",
      "target": "AI infrastructure",
      "direction": "bullish",
      "confidence": 0.65,
      "score": 8.5,
      "horizon": "1-3 trading days",
      "drivers": ["AI", "cooling demand"],
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
        session: requests.Session | None = None,
        timeout: int = 10,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.base_url = base_url.rstrip("/")
        self.model = model
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
        symbols: list[str] | None = None,
    ) -> dict[str, Any]:
        context = {
            "items": items[:30],
            "keywords": keywords[:20],
            "sectorHints": sector_hints[:12],
            "symbols": list(symbols or []),
        }
        metadata_base = self._build_metadata_base(context)
        cache_key = self._build_cache_key(context, metadata_base["inputDigest"])

        if not self.api_key:
            return self._heuristic_prediction(
                context=context,
                metadata_base=metadata_base,
                cache_key=cache_key,
                warnings=["DeepSeek API key is not configured; using local heuristic predictions."],
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
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
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
                },
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
                    "DeepSeek prediction failed; using local heuristic: "
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

        for hint in context["sectorHints"][:5]:
            score = float(hint.get("score") or 0.0)
            confidence = max(0.25, min(0.78, 0.35 + score / 20))
            matched = [str(item) for item in hint.get("matchedKeywords") or [] if str(item)]
            predictions.append(
                {
                    "targetType": "sector",
                    "target": str(hint.get("name") or "unknown"),
                    "direction": "bullish" if score >= 2 else "neutral",
                    "confidence": round(confidence, 2),
                    "score": score,
                    "horizon": "1-3 trading days",
                    "drivers": matched[:5] or ["sector keyword match"],
                    "sourceIds": source_ids,
                }
            )

        if not predictions:
            for keyword in context["keywords"][:5]:
                count = float(keyword.get("count") or 0.0)
                predictions.append(
                    {
                        "targetType": "theme",
                        "target": str(keyword.get("keyword") or "unknown"),
                        "direction": "neutral",
                        "confidence": round(max(0.2, min(0.6, 0.25 + count / 30)), 2),
                        "score": count,
                        "horizon": "1-3 trading days",
                        "drivers": [str(keyword.get("keyword") or "keyword frequency")],
                        "sourceIds": source_ids,
                    }
                )

        if not predictions:
            predictions.append(
                {
                    "targetType": "market",
                    "target": "A-share broad market",
                    "direction": "neutral",
                    "confidence": 0.2,
                    "score": 0.0,
                    "horizon": "1-3 trading days",
                    "drivers": ["insufficient market news context"],
                    "sourceIds": source_ids,
                }
            )

        return {
            "predictionMetadata": {
                "provider": "local_heuristic",
                "model": "keyword-sector-rules",
                "degraded": True,
                "cached": False,
                "cacheKey": cache_key,
                **metadata_base,
                "warnings": warnings,
            },
            "predictions": predictions,
            "predictionSummary": (
                "Local heuristic prediction derived from keyword frequency and sector hints."
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
                    "horizon": str(row.get("horizon") or "1-3 trading days"),
                    "drivers": _string_list(row.get("drivers")),
                    "sourceIds": _string_list(row.get("sourceIds")),
                }
            )
        return predictions[:8]

    def _normalize_risk_notes(self, value: Any) -> list[str]:
        notes = _string_list(value)
        return notes or self._default_risk_notes()

    def _build_metadata_base(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "schemaVersion": PREDICTION_SCHEMA_VERSION,
            "inputDigest": _digest_payload(context),
            "newsItemCount": len(context["items"]),
            "keywordCount": len(context["keywords"]),
            "sectorHintCount": len(context["sectorHints"]),
            "symbolCount": len(context["symbols"]),
        }

    def _build_cache_key(self, context: dict[str, Any], input_digest: str) -> str:
        cache_payload = {
            "model": self.model,
            "schemaVersion": PREDICTION_SCHEMA_VERSION,
            "inputDigest": input_digest,
            "symbols": context["symbols"],
        }
        return _digest_payload(cache_payload)

    def _default_risk_notes(self) -> list[str]:
        return [
            "Predictions are research context, not investment advice.",
            "Validate candidate symbols with AKQuant backtests and broader market data.",
            "External news and model outputs may be incomplete, delayed, or wrong.",
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
