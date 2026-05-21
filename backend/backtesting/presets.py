from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StrategyPreset:
    id: str
    label: str
    description: str
    summary: str
    use_case: str
    risk_notes: str
    code: str
    default_params: dict[str, Any] = field(default_factory=dict)
    parameter_schema: list[dict[str, Any]] = field(default_factory=list)


MA_CROSS_CODE = """def generate_signals(data, ctx):
    fast_window = int(ctx.params.get("fast_window", 5))
    slow_window = int(ctx.params.get("slow_window", 20))

    close = data["close"]
    fast = ctx.sma(close, fast_window)
    slow = ctx.sma(close, slow_window)

    signal = ctx.new_signal()
    signal[ctx.cross_over(fast, slow)] = 1
    signal[ctx.cross_under(fast, slow)] = 0
    return signal.ffill().fillna(0)
"""


RSI_REVERSION_CODE = """def generate_signals(data, ctx):
    window = int(ctx.params.get("window", 14))
    oversold = float(ctx.params.get("oversold", 30))
    overbought = float(ctx.params.get("overbought", 70))

    rsi = ctx.rsi(data["close"], window)
    signal = ctx.new_signal()
    signal[rsi <= oversold] = 1
    signal[rsi >= overbought] = 0
    return signal.ffill().fillna(0)
"""


BREAKOUT_CHANNEL_CODE = """def generate_signals(data, ctx):
    window = int(ctx.params.get("window", 20))
    breakout = data["close"] > data["high"].rolling(window).max().shift(1)
    exit_line = data["close"] < data["low"].rolling(window).min().shift(1)

    signal = ctx.new_signal()
    signal[breakout] = 1
    signal[exit_line] = 0
    return signal.ffill().fillna(0)
"""


EVENT_THEME_MOMENTUM_CODE = """def generate_signals(data, ctx):
    lookback_window = int(ctx.params.get("lookback_window", 20))
    volume_window = int(ctx.params.get("volume_window", 5))
    volume_multiplier = float(ctx.params.get("volume_multiplier", 1.2))

    close = data["close"]
    high_breakout = close > data["high"].rolling(lookback_window).max().shift(1)
    volume_trend = data["volume"] > data["volume"].rolling(volume_window).mean() * volume_multiplier
    exit_line = close < close.rolling(max(5, lookback_window // 2)).mean()

    signal = ctx.new_signal()
    signal[high_breakout & volume_trend] = 1
    signal[exit_line] = 0
    return signal.ffill().fillna(0)
"""


PRESETS: dict[str, StrategyPreset] = {
    "ma_cross": StrategyPreset(
        id="ma_cross",
        label="双均线策略",
        description="AKQuant-backed moving average crossover preset.",
        summary="用快慢均线交叉寻找趋势启动与结束区间。",
        use_case="适合趋势较明确、希望用简单参数快速验证方向的日线研究场景。",
        risk_notes="震荡市里容易反复打脸，建议搭配成本与止损设置一起评估。",
        code=MA_CROSS_CODE,
        default_params={"fast_window": 5, "slow_window": 20},
        parameter_schema=[
            {
                "name": "fast_window",
                "label": "快线窗口",
                "type": "number",
                "group": "trend",
                "helpText": "更短的窗口会更敏感，也更容易在震荡里产生噪声。",
                "default": 5,
                "min": 2,
                "max": 60,
                "step": 1,
            },
            {
                "name": "slow_window",
                "label": "慢线窗口",
                "type": "number",
                "group": "trend",
                "helpText": "更长的窗口更稳定，但信号确认会更慢。",
                "default": 20,
                "min": 5,
                "max": 120,
                "step": 1,
            },
        ],
    ),
    "rsi_reversion": StrategyPreset(
        id="rsi_reversion",
        label="RSI 反转策略",
        description="Buy on oversold RSI and exit on overbought RSI.",
        summary="在超卖位置尝试逆向买入，在超买位置离场。",
        use_case="适合希望研究震荡回归、而非趋势追涨的回测场景。",
        risk_notes="单边趋势下可能持续逆势，建议同时观察最大回撤和止损触发。",
        code=RSI_REVERSION_CODE,
        default_params={"window": 14, "oversold": 30, "overbought": 70},
        parameter_schema=[
            {
                "name": "window",
                "label": "RSI 窗口",
                "type": "number",
                "group": "momentum",
                "helpText": "窗口越短，RSI 波动越大，进出场会更频繁。",
                "default": 14,
                "min": 5,
                "max": 60,
                "step": 1,
            },
            {
                "name": "oversold",
                "label": "超卖阈值",
                "type": "number",
                "group": "threshold",
                "helpText": "阈值越高越容易触发抄底，信号数量也会更多。",
                "default": 30,
                "min": 5,
                "max": 50,
                "step": 1,
            },
            {
                "name": "overbought",
                "label": "超买阈值",
                "type": "number",
                "group": "threshold",
                "helpText": "阈值越低越容易触发卖出，持有周期通常更短。",
                "default": 70,
                "min": 50,
                "max": 95,
                "step": 1,
            },
        ],
    ),
    "breakout_channel": StrategyPreset(
        id="breakout_channel",
        label="通道突破策略",
        description="Enter on channel breakout and exit on channel breakdown.",
        summary="突破近期高点时入场，跌破近期低点时离场。",
        use_case="适合研究事件驱动或强势板块中的突破延续行情。",
        risk_notes="假突破环境下会产生较多无效交易，需结合滑点和成本一起看。",
        code=BREAKOUT_CHANNEL_CODE,
        default_params={"window": 20},
        parameter_schema=[
            {
                "name": "window",
                "label": "通道窗口",
                "type": "number",
                "group": "breakout",
                "helpText": "窗口越大，突破门槛越高，信号更少但更偏中期趋势。",
                "default": 20,
                "min": 5,
                "max": 120,
                "step": 1,
            }
        ],
    ),
    "event_theme_momentum": StrategyPreset(
        id="event_theme_momentum",
        label="Event theme momentum",
        description="Validate news-predicted themes with breakout and volume confirmation.",
        summary=(
            "Uses recent high breakout plus volume confirmation to test whether a "
            "news-driven candidate has follow-through."
        ),
        use_case=(
            "Designed for symbols or sectors surfaced by the market-news prediction endpoint; "
            "use it as validation context after a theme is detected."
        ),
        risk_notes=(
            "Event-driven breakouts can reverse quickly after news fades. Review drawdown, "
            "turnover, and costs before trusting any prediction."
        ),
        code=EVENT_THEME_MOMENTUM_CODE,
        default_params={
            "lookback_window": 20,
            "volume_window": 5,
            "volume_multiplier": 1.2,
        },
        parameter_schema=[
            {
                "name": "lookback_window",
                "label": "Lookback window",
                "type": "number",
                "group": "event",
                "helpText": "Higher values require stronger price breakout confirmation.",
                "default": 20,
                "min": 5,
                "max": 120,
                "step": 1,
            },
            {
                "name": "volume_window",
                "label": "Volume window",
                "type": "number",
                "group": "event",
                "helpText": "Short rolling window used to judge whether event volume is elevated.",
                "default": 5,
                "min": 2,
                "max": 30,
                "step": 1,
            },
            {
                "name": "volume_multiplier",
                "label": "Volume multiplier",
                "type": "number",
                "group": "event",
                "helpText": "Volume must exceed the rolling average by this multiple.",
                "default": 1.2,
                "min": 1,
                "max": 5,
                "step": 0.1,
            },
        ],
    ),
}


def list_strategy_presets() -> list[StrategyPreset]:
    return list(PRESETS.values())


def get_strategy_preset(preset_id: str | None) -> StrategyPreset | None:
    if not preset_id:
        return None
    return PRESETS.get(preset_id)


def serialize_strategy_preset(preset: StrategyPreset) -> dict[str, Any]:
    return {
        "id": preset.id,
        "label": preset.label,
        "description": preset.description,
        "summary": preset.summary,
        "useCase": preset.use_case,
        "riskNotes": preset.risk_notes,
        "defaultParams": dict(preset.default_params),
        "parameterSchema": [dict(item) for item in preset.parameter_schema],
        "code": preset.code,
    }


def serialize_strategy_presets() -> dict[str, list[dict[str, Any]]]:
    return {"items": [serialize_strategy_preset(preset) for preset in list_strategy_presets()]}


def resolve_strategy_source(
    *,
    mode: str = "custom",
    preset_id: str | None = None,
    custom_code: str | None = None,
) -> tuple[str, StrategyPreset | None]:
    if mode == "preset":
        preset = get_strategy_preset(preset_id)
        if preset is None:
            raise ValueError(f"未知策略预设: {preset_id}")
        return preset.code, preset

    code = (custom_code or "").strip()
    if not code and preset_id:
        preset = get_strategy_preset(preset_id)
        if preset is not None:
            return preset.code, preset
    if not code:
        raise ValueError("自定义策略模式下必须提供 strategyCode")
    return code, None
