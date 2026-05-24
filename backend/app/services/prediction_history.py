from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deepseek_prediction import _digest_payload

SYMBOL_RE = re.compile(r"\b\d{6}\b")


class PredictionHistoryService:
    def __init__(self, path: str | Path, *, max_records: int = 200) -> None:
        self.path = Path(path)
        self.max_records = max(1, max_records)

    def store_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        created_at = datetime.now(UTC).isoformat(timespec="seconds")
        run_id = _build_run_id(payload, created_at)
        predictions = [
            {
                **prediction,
                "predictionId": prediction.get("predictionId")
                or f"{run_id}-{index + 1:02d}",
            }
            for index, prediction in enumerate(payload.get("predictions") or [])
        ]
        record = {
            "runId": run_id,
            "createdAt": created_at,
            "source": payload.get("source"),
            "requestedLimit": payload.get("requestedLimit"),
            "degraded": bool(payload.get("degraded")),
            "warnings": payload.get("warnings") or [],
            "channels": payload.get("channels") or [],
            "items": payload.get("items") or [],
            "keywords": payload.get("keywords") or [],
            "sectorHints": payload.get("sectorHints") or [],
            "eventHints": payload.get("eventHints") or [],
            "sourceQuality": payload.get("sourceQuality") or {},
            "dedupeMetadata": payload.get("dedupeMetadata") or {},
            "predictionMetadata": payload.get("predictionMetadata") or {},
            "predictionSummary": payload.get("predictionSummary") or "",
            "predictions": predictions,
            "riskNotes": payload.get("riskNotes") or [],
            "backtestHandoff": payload.get("backtestHandoff") or {},
        }
        self._append(record)
        return record

    def list_runs(self, limit: int = 20) -> dict[str, Any]:
        rows, warnings = self._read_records()
        limited_rows = rows[: max(1, min(limit, self.max_records))]
        return {
            "items": [_compact_run(row) for row in limited_rows],
            "metadata": {
                "source": "local_jsonl",
                "degraded": bool(warnings),
                "warnings": warnings,
                "totalReadable": len(rows),
            },
        }

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        rows, _warnings = self._read_records()
        for row in rows:
            if row.get("runId") == run_id:
                return row
        return None

    def evaluate_run(self, run_id: str, market_data_service: Any) -> dict[str, Any] | None:
        run = self.get_run(run_id)
        if run is None:
            return None

        predictions = run.get("predictions") or []
        symbols = sorted(
            {
                symbol
                for prediction in predictions
                for symbol in _extract_symbols(prediction)
            }
        )
        quote_map: dict[str, dict[str, Any]] = {}
        warnings: list[str] = []
        if symbols:
            try:
                quote_payload = market_data_service.get_quotes(symbols)
                quote_map = {
                    str(item.get("symbol")): item
                    for item in quote_payload.get("items") or []
                    if item.get("symbol")
                }
            except Exception as error:
                warnings.append(
                    f"行情评估失败，已将可评估预测标记为待观察：{error.__class__.__name__}: {error}"
                )

        evaluation_items = [
            _evaluate_prediction(prediction, quote_map)
            for prediction in predictions
        ]
        assessable = [
            item
            for item in evaluation_items
            if item["status"] in {"hit", "miss", "neutral"}
        ]
        positive = [item for item in assessable if item["status"] in {"hit", "neutral"}]
        summary = {
            "total": len(evaluation_items),
            "assessable": len(assessable),
            "hit": sum(1 for item in evaluation_items if item["status"] == "hit"),
            "miss": sum(1 for item in evaluation_items if item["status"] == "miss"),
            "neutral": sum(1 for item in evaluation_items if item["status"] == "neutral"),
            "pending": sum(1 for item in evaluation_items if item["status"] == "pending"),
            "hitRate": round(len(positive) / len(assessable), 4) if assessable else None,
        }
        return {
            "runId": run_id,
            "evaluatedAt": datetime.now(UTC).isoformat(timespec="seconds"),
            "evaluationSummary": summary,
            "evaluationItems": evaluation_items,
            "metadata": {
                "source": "latest_quotes",
                "degraded": bool(warnings),
                "warnings": warnings,
            },
        }

    def _append(self, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
        self._truncate()

    def _truncate(self) -> None:
        if not self.path.exists():
            return
        lines = self.path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= self.max_records:
            return
        self.path.write_text(
            "\n".join(lines[-self.max_records :]) + "\n",
            encoding="utf-8",
        )

    def _read_records(self) -> tuple[list[dict[str, Any]], list[str]]:
        if not self.path.exists():
            return [], []
        rows: list[dict[str, Any]] = []
        warnings: list[str] = []
        for line_number, line in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f"预测历史第 {line_number} 行无法解析，已跳过。")
                continue
            if isinstance(value, dict):
                rows.append(value)
        rows.sort(key=lambda item: str(item.get("createdAt") or ""), reverse=True)
        return rows, warnings


def _build_run_id(payload: dict[str, Any], created_at: str) -> str:
    metadata = payload.get("predictionMetadata") or {}
    digest = _digest_payload(
        {
            "createdAt": created_at,
            "cacheKey": metadata.get("cacheKey"),
            "inputDigest": metadata.get("inputDigest"),
            "predictionCount": len(payload.get("predictions") or []),
        }
    )
    return f"pred_{digest}"


def _compact_run(row: dict[str, Any]) -> dict[str, Any]:
    metadata = row.get("predictionMetadata") or {}
    source_quality = row.get("sourceQuality") or {}
    return {
        "runId": row.get("runId"),
        "createdAt": row.get("createdAt"),
        "provider": metadata.get("provider"),
        "model": metadata.get("model"),
        "thinkingType": metadata.get("thinkingType"),
        "reasoningEffort": metadata.get("reasoningEffort"),
        "degraded": bool(metadata.get("degraded") or row.get("degraded")),
        "predictionCount": len(row.get("predictions") or []),
        "qualityScore": source_quality.get("qualityScore"),
        "summary": row.get("predictionSummary") or "",
    }


def _extract_symbols(prediction: dict[str, Any]) -> list[str]:
    target = str(prediction.get("target") or "")
    return SYMBOL_RE.findall(target)


def _evaluate_prediction(
    prediction: dict[str, Any],
    quote_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    prediction_id = str(prediction.get("predictionId") or "")
    target = str(prediction.get("target") or "")
    direction = str(prediction.get("direction") or "neutral")
    symbols = _extract_symbols(prediction)
    if not symbols:
        return {
            "predictionId": prediction_id,
            "target": target,
            "direction": direction,
            "status": "pending",
            "actualChangePercent": None,
            "note": "预测对象不是明确股票代码，暂不做方向命中评估。",
        }
    symbol = symbols[0]
    quote = quote_map.get(symbol)
    if not quote or not isinstance(quote.get("changePercent"), (int, float)):
        return {
            "predictionId": prediction_id,
            "target": target,
            "direction": direction,
            "status": "pending",
            "actualChangePercent": None,
            "note": f"{symbol} 暂无可用涨跌幅，等待后续评估。",
        }

    change = float(quote["changePercent"])
    if direction == "bullish":
        status = "hit" if change > 0 else "miss"
    elif direction == "bearish":
        status = "hit" if change < 0 else "miss"
    else:
        status = "neutral" if abs(change) < 0.5 else "miss"

    return {
        "predictionId": prediction_id,
        "target": target,
        "direction": direction,
        "status": status,
        "actualChangePercent": change,
        "note": f"{symbol} 最新涨跌幅 {change:.2f}%。",
    }
