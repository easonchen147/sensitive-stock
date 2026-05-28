from __future__ import annotations

import json
from time import perf_counter
from typing import Any

import pandas as pd
import requests

from backtesting.indicators import bollinger_bands, macd, rsi, sma
from ..schemas.research import DiagnosisRequest
from .deepseek_prediction import DeepSeekMarketPredictionService
from .stock_detail import StockDetailService

DEEPSEEK_SYSTEM_PROMPT = """你是谨慎的 A 股个股诊断研究助手。
只返回严格 JSON，不给出交易指令或收益保证。
所有可读文本必须使用简体中文。
输出 JSON 结构：
{
  "sections": [
    {"title": "市场背景", "content": "..."},
    {"title": "技术分析", "content": "..."},
    {"title": "基本面摘要", "content": "..."},
    {"title": "AI 洞察", "content": "..."},
    {"title": "风险提示", "content": "..."}
  ]
}"""


class DiagnosisService:
    def __init__(
        self,
        market_data_service: Any | None = None,
        stock_detail_service: StockDetailService | None = None,
        deepseek_service: DeepSeekMarketPredictionService | None = None,
    ) -> None:
        self.market_data_service = market_data_service
        self.stock_detail_service = stock_detail_service or StockDetailService()
        self.deepseek_service = deepseek_service

    def describe(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "sections": [
                "market_context",
                "technical_indicators",
                "fundamentals",
                "ai_insight",
                "risk_notes",
            ],
            "metadata": {
                "source": "akshare+deepseek",
                "degraded": False,
            },
        }

    def run(self, request: DiagnosisRequest) -> dict[str, Any]:
        symbol = request.symbol
        warnings: list[str] = []
        unavailable_inputs: list[str] = []
        source = "akshare"

        # ---- 1. Fetch stock detail ----
        detail: dict[str, Any] = {}
        try:
            detail = self.stock_detail_service.get_stock_detail(symbol)
            if detail.get("degraded"):
                unavailable_inputs.append("stock_detail")
                if detail.get("error"):
                    warnings.append(f"个股详情部分不可用：{detail['error']}")
        except Exception as error:
            unavailable_inputs.append("stock_detail")
            warnings.append(f"个股详情获取失败：{error}")

        name = detail.get("name") or symbol
        industry = detail.get("industry") or ""
        price = _to_float(detail.get("price"))
        change_percent = _to_float(detail.get("changePercent"))
        pe = _to_float(detail.get("pe"))
        pb = _to_float(detail.get("pb"))
        turnover_rate = _to_float(detail.get("turnoverRate"))
        volume_ratio = _to_float(detail.get("volumeRatio"))
        market_cap = _to_float(detail.get("marketCap"))
        amount = _to_float(detail.get("amount"))

        # ---- 2. Fetch K-line data (last 60 trading days) ----
        kline_items: list[dict[str, Any]] = []
        try:
            kline_payload = self.stock_detail_service.get_kline_data(symbol, "daily")
            kline_items = kline_payload.get("items", [])
            if kline_payload.get("degraded"):
                unavailable_inputs.append("kline_data")
                if kline_payload.get("error"):
                    warnings.append(f"K 线数据部分不可用：{kline_payload['error']}")
        except Exception as error:
            unavailable_inputs.append("kline_data")
            warnings.append(f"K 线数据获取失败：{error}")

        # Use last 60 bars
        kline_items = kline_items[-60:]

        # ---- 3. Compute technical indicators ----
        indicators: list[dict[str, Any]] = []
        technical_scores: dict[str, Any] = {}

        if len(kline_items) >= 20:
            closes = pd.Series(
                [_to_float(bar.get("close")) for bar in kline_items],
                dtype=float,
            )
            volumes = pd.Series(
                [_to_float(bar.get("volume")) for bar in kline_items],
                dtype=float,
            )

            # Moving averages
            ma_values = {}
            for period in (5, 10, 20, 60):
                if len(closes) >= period:
                    ma_series = sma(closes, period)
                    ma_val = round(ma_series.iloc[-1], 3)
                    if pd.notna(ma_val):
                        ma_key = f"MA{period}"
                        ma_values[ma_key] = ma_val
                        tone = _ma_signal(price, ma_val)
                        indicators.append({
                            "name": ma_key.lower(),
                            "label": f"{period} 日均线",
                            "value": ma_val,
                            "tone": tone,
                        })

            # RSI(14)
            rsi_val = None
            if len(closes) >= 14:
                rsi_series = rsi(closes, 14)
                rsi_val = round(rsi_series.iloc[-1], 2) if pd.notna(rsi_series.iloc[-1]) else None
                if rsi_val is not None:
                    rsi_tone = _rsi_signal(rsi_val)
                    indicators.append({
                        "name": "rsi14",
                        "label": "RSI(14)",
                        "value": rsi_val,
                        "tone": rsi_tone,
                    })

            # MACD(12, 26, 9)
            macd_val, macd_signal_val, macd_hist = None, None, None
            if len(closes) >= 26:
                macd_df = macd(closes, 12, 26, 9)
                macd_val = round(macd_df["macd"].iloc[-1], 4) if pd.notna(macd_df["macd"].iloc[-1]) else None
                macd_signal_val = round(macd_df["signal"].iloc[-1], 4) if pd.notna(macd_df["signal"].iloc[-1]) else None
                macd_hist = round(macd_df["hist"].iloc[-1], 4) if pd.notna(macd_df["hist"].iloc[-1]) else None
                if macd_val is not None:
                    macd_tone = "bullish" if macd_hist is not None and macd_hist > 0 else "bearish" if macd_hist is not None and macd_hist < 0 else "neutral"
                    indicators.append({
                        "name": "macd",
                        "label": "MACD(12,26,9)",
                        "value": macd_val,
                        "signal": macd_signal_val,
                        "hist": macd_hist,
                        "tone": macd_tone,
                    })

            # Bollinger Bands(20, 2)
            bb_upper, bb_mid, bb_lower = None, None, None
            if len(closes) >= 20:
                bb_df = bollinger_bands(closes, 20, 2)
                bb_upper = round(bb_df["upper"].iloc[-1], 3) if pd.notna(bb_df["upper"].iloc[-1]) else None
                bb_mid = round(bb_df["mid"].iloc[-1], 3) if pd.notna(bb_df["mid"].iloc[-1]) else None
                bb_lower = round(bb_df["lower"].iloc[-1], 3) if pd.notna(bb_df["lower"].iloc[-1]) else None
                if bb_upper is not None and bb_lower is not None and price > 0:
                    if price >= bb_upper:
                        bb_tone = "bearish"
                    elif price <= bb_lower:
                        bb_tone = "bullish"
                    else:
                        bb_tone = "neutral"
                    indicators.append({
                        "name": "bollinger",
                        "label": "布林带(20,2)",
                        "value": {"upper": bb_upper, "mid": bb_mid, "lower": bb_lower},
                        "tone": bb_tone,
                    })

            # Volume ratio (today / 20-day avg)
            computed_vol_ratio = None
            if len(volumes) >= 20:
                avg_vol = volumes.iloc[-20:].mean()
                today_vol = volumes.iloc[-1]
                if avg_vol > 0:
                    computed_vol_ratio = round(today_vol / avg_vol, 2)
                    indicators.append({
                        "name": "volume_ratio",
                        "label": "量比(20日)",
                        "value": computed_vol_ratio,
                        "tone": "positive" if computed_vol_ratio > 1.5 else "warning" if computed_vol_ratio < 0.5 else "neutral",
                    })

            # Build technical_scores
            technical_scores = _build_technical_scores(
                price=price,
                ma_values=ma_values,
                rsi_val=rsi_val,
                macd_hist=macd_hist,
                bb_upper=bb_upper,
                bb_lower=bb_lower,
                volume_ratio=computed_vol_ratio or volume_ratio,
            )
        else:
            unavailable_inputs.append("technical_indicators")
            warnings.append("K 线数据不足，无法计算技术指标。")

        # Trend tone
        trend_tone = "positive" if change_percent >= 0 else "warning"

        # ---- 4. Build AI prompt and call DeepSeek ----
        ai_analysis: dict[str, Any] | None = None
        ai_sections: list[dict[str, Any]] | None = None

        if self.deepseek_service and self.deepseek_service.api_key:
            prompt = _build_diagnosis_prompt(
                name=name,
                symbol=symbol,
                industry=industry,
                price=price,
                change_percent=change_percent,
                pe=pe,
                pb=pb,
                turnover_rate=turnover_rate,
                volume_ratio=volume_ratio or computed_vol_ratio,
                market_cap=market_cap,
                amount=amount,
                indicators=indicators,
                kline_items=kline_items,
            )
            try:
                ai_analysis = self._call_deepseek(prompt)
                ai_sections = ai_analysis.get("sections")
            except Exception as error:
                warnings.append(f"AI 诊断失败，已切换为本地分析：{error}")

        # ---- 5. Build sections ----
        if ai_sections and isinstance(ai_sections, list):
            sections = [
                {
                    "title": section.get("title", ""),
                    "tone": "neutral",
                    "summary": section.get("content", ""),
                    "source": "deepseek",
                }
                for section in ai_sections
                if isinstance(section, dict)
            ]
        else:
            sections = _build_fallback_sections(
                name=name,
                symbol=symbol,
                price=price,
                change_percent=change_percent,
                trend_tone=trend_tone,
                indicators=indicators,
                industry=industry,
                pe=pe,
                pb=pb,
            )

        # ---- 6. Assemble response ----
        degraded = bool(unavailable_inputs)
        risk_notes = [
            "本报告只作为研究上下文，不构成投资建议。",
            "技术指标信号可能因市场突发事件而失效。",
            "诊断结论需要结合回测结果和更宽的市场背景验证。",
        ]

        return {
            "symbol": symbol,
            "name": name,
            "industry": industry,
            "marketContext": {
                "price": price,
                "changePercent": change_percent,
                "pe": pe,
                "pb": pb,
                "turnoverRate": turnover_rate,
                "volumeRatio": volume_ratio or computed_vol_ratio,
                "marketCap": market_cap,
                "amount": amount,
                "source": source,
            },
            "indicators": indicators,
            "technicalScores": technical_scores,
            "sections": sections,
            "aiAnalysis": ai_analysis,
            "riskNotes": risk_notes,
            "metadata": {
                "source": source,
                "degraded": degraded,
                "unavailableInputs": unavailable_inputs,
                "warnings": warnings,
            },
        }

    def _call_deepseek(self, prompt: str) -> dict[str, Any]:
        """Call DeepSeek chat API for structured diagnosis."""
        api_key = self.deepseek_service.api_key
        base_url = self.deepseek_service.base_url
        model = self.deepseek_service.model
        timeout = self.deepseek_service.timeout

        started_at = perf_counter()
        request_payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
            "response_format": {"type": "json_object"},
        }

        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=request_payload,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        content = (
            (payload.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        parsed = json.loads(content)
        parsed["_meta"] = {
            "provider": "deepseek",
            "model": model,
            "latencyMs": round((perf_counter() - started_at) * 1000),
        }
        return parsed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_float(value: Any) -> float | None:
    try:
        if value in ("", None, "-"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _ma_signal(price: float, ma_val: float) -> str:
    if price <= 0 or ma_val <= 0:
        return "neutral"
    diff_pct = (price - ma_val) / ma_val * 100
    if diff_pct > 2:
        return "bullish"
    if diff_pct < -2:
        return "bearish"
    return "neutral"


def _rsi_signal(rsi_val: float) -> str:
    if rsi_val >= 70:
        return "bearish"  # overbought
    if rsi_val <= 30:
        return "bullish"  # oversold
    if rsi_val >= 60:
        return "warning"
    if rsi_val <= 40:
        return "positive"
    return "neutral"


def _build_technical_scores(
    *,
    price: float,
    ma_values: dict[str, float],
    rsi_val: float | None,
    macd_hist: float | None,
    bb_upper: float | None,
    bb_lower: float | None,
    volume_ratio: float | None,
) -> dict[str, Any]:
    scores: dict[str, Any] = {}

    # MA score: count how many MAs price is above
    ma_above = 0
    ma_total = 0
    for key, val in ma_values.items():
        ma_total += 1
        if price > val:
            ma_above += 1
    if ma_total > 0:
        scores["ma"] = {"above": ma_above, "total": ma_total, "score": round(ma_above / ma_total, 2)}

    # RSI score
    if rsi_val is not None:
        # Normalize RSI to 0-1 (0=oversold bullish, 1=overbought bearish)
        scores["rsi"] = {"value": rsi_val, "score": round(1 - rsi_val / 100, 2)}

    # MACD score
    if macd_hist is not None:
        scores["macd"] = {"hist": macd_hist, "score": 1 if macd_hist > 0 else 0}

    # Bollinger score
    if bb_upper is not None and bb_lower is not None and price > 0:
        bb_range = bb_upper - bb_lower
        if bb_range > 0:
            bb_position = (price - bb_lower) / bb_range
            scores["bollinger"] = {"position": round(bb_position, 2), "score": round(1 - bb_position, 2)}

    # Volume score
    if volume_ratio is not None:
        scores["volume"] = {"ratio": volume_ratio, "score": round(min(volume_ratio / 2, 1.0), 2)}

    # Composite score
    component_scores = [v["score"] for v in scores.values() if isinstance(v, dict) and "score" in v]
    if component_scores:
        scores["composite"] = round(sum(component_scores) / len(component_scores), 2)

    return scores


def _build_diagnosis_prompt(
    *,
    name: str,
    symbol: str,
    industry: str,
    price: float,
    change_percent: float,
    pe: float,
    pb: float,
    turnover_rate: float,
    volume_ratio: float | None,
    market_cap: float,
    amount: float,
    indicators: list[dict[str, Any]],
    kline_items: list[dict[str, Any]],
) -> str:
    # Recent 5-day price trend
    recent_closes = [_to_float(bar.get("close")) for bar in kline_items[-5:] if bar.get("close")]
    if len(recent_closes) >= 2:
        trend_direction = "上涨" if recent_closes[-1] > recent_closes[0] else "下跌" if recent_closes[-1] < recent_closes[0] else "横盘"
        trend_pct = round((recent_closes[-1] - recent_closes[0]) / recent_closes[0] * 100, 2) if recent_closes[0] else 0
        trend_desc = f"近 5 日累计{trend_direction} {trend_pct}%"
    else:
        trend_desc = "近期趋势数据不足"

    # Format indicator lines
    indicator_lines: list[str] = []
    for ind in indicators:
        name_str = ind.get("label", ind.get("name", ""))
        val = ind.get("value")
        tone = ind.get("tone", "neutral")
        if isinstance(val, dict):
            val_str = ", ".join(f"{k}={v}" for k, v in val.items())
        else:
            val_str = str(val)
        indicator_lines.append(f"- {name_str}: {val_str}（信号：{tone}）")
    indicator_block = "\n".join(indicator_lines) if indicator_lines else "- 暂无技术指标数据"

    market_cap_yi = round(market_cap / 1e8, 2) if market_cap else 0
    amount_yi = round(amount / 1e8, 2) if amount else 0

    prompt = f"""请对以下 A 股个股进行诊断分析，返回包含 5 个 section 的 JSON：

## 个股信息
- 股票：{name}（{symbol}）
- 所属行业：{industry}
- 最新价：{price}，涨跌幅：{change_percent}%
- 市盈率 PE：{pe}，市净率 PB：{pb}
- 换手率：{turnover_rate}%，量比：{volume_ratio or 'N/A'}
- 总市值：{market_cap_yi} 亿元，成交额：{amount_yi} 亿元

## 技术指标
{indicator_block}

## 近期走势
{trend_desc}

请从市场背景、技术分析、基本面摘要、AI 洞察、风险提示五个维度给出结构化诊断意见。每个 section 使用 title 和 content 字段，content 控制在 2-4 句话。"""

    return prompt


def _build_fallback_sections(
    *,
    name: str,
    symbol: str,
    price: float,
    change_percent: float,
    trend_tone: str,
    indicators: list[dict[str, Any]],
    industry: str,
    pe: float,
    pb: float,
) -> list[dict[str, Any]]:
    """Build heuristic sections when DeepSeek is unavailable."""
    sections: list[dict[str, Any]] = []

    # Market context
    sections.append({
        "title": "市场背景",
        "tone": trend_tone,
        "summary": (
            f"{name}（{symbol}）所属行业为 {industry}，"
            f"最新报价 {price:.2f}，涨跌幅 {change_percent:.2f}%。"
        ),
    })

    # Technical analysis
    tech_parts: list[str] = []
    bullish_count = 0
    bearish_count = 0
    for ind in indicators:
        tone = ind.get("tone", "neutral")
        if tone in ("bullish", "positive"):
            bullish_count += 1
        elif tone in ("bearish", "warning"):
            bearish_count += 1
    if bullish_count > bearish_count:
        tech_parts.append("多数技术指标呈偏多信号。")
    elif bearish_count > bullish_count:
        tech_parts.append("多数技术指标呈偏空信号。")
    else:
        tech_parts.append("技术指标信号多空交织，方向不明确。")

    for ind in indicators:
        label = ind.get("label", ind.get("name"))
        val = ind.get("value")
        if isinstance(val, dict):
            val_str = ", ".join(f"{k}={v}" for k, v in val.items())
        else:
            val_str = str(val)
        tech_parts.append(f"{label} = {val_str}。")

    sections.append({
        "title": "技术分析",
        "tone": "positive" if bullish_count > bearish_count else "warning" if bearish_count > bullish_count else "neutral",
        "summary": " ".join(tech_parts) if tech_parts else "技术数据不足，无法完成分析。",
    })

    # Fundamentals
    fund_parts: list[str] = []
    if pe > 0:
        fund_parts.append(f"市盈率 {pe:.2f}。")
    if pb > 0:
        fund_parts.append(f"市净率 {pb:.2f}。")
    if industry:
        fund_parts.append(f"所属行业为 {industry}。")
    sections.append({
        "title": "基本面摘要",
        "tone": "neutral",
        "summary": " ".join(fund_parts) if fund_parts else "基本面数据暂不可用。",
    })

    # AI Insight (heuristic)
    if bullish_count > bearish_count:
        insight = "从技术面看短线偏多，但需关注成交量配合和消息面变化。"
        insight_tone = "positive"
    elif bearish_count > bullish_count:
        insight = "从技术面看短线偏空，建议注意防守并控制仓位。"
        insight_tone = "warning"
    else:
        insight = "当前技术面信号模糊，建议等待更明确的方向信号再做判断。"
        insight_tone = "neutral"
    sections.append({
        "title": "AI 洞察",
        "tone": insight_tone,
        "summary": insight,
    })

    # Risk notes
    sections.append({
        "title": "风险提示",
        "tone": "neutral",
        "summary": "本报告只作为研究上下文，不构成投资建议。诊断结论需要结合回测结果和更宽的市场背景验证。",
    })

    return sections
