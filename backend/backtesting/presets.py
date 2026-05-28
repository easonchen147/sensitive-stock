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


MACD_TREND_CODE = """def generate_signals(data, ctx):
    fast = int(ctx.params.get("fast_period", 12))
    slow = int(ctx.params.get("slow_period", 26))
    signal_period = int(ctx.params.get("signal_period", 9))

    close = data["close"]
    fast_ema = ctx.ema(close, fast)
    slow_ema = ctx.ema(close, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ctx.ema(macd_line, signal_period)

    signal = ctx.new_signal()
    signal[ctx.cross_over(macd_line, signal_line)] = 1
    signal[ctx.cross_under(macd_line, signal_line)] = 0
    return signal.ffill().fillna(0)
"""


BOLLINGER_REVERSION_CODE = """def generate_signals(data, ctx):
    window = int(ctx.params.get("window", 20))
    num_std = float(ctx.params.get("num_std", 2.0))

    close = data["close"]
    mid = ctx.sma(close, window)
    std = close.rolling(window=window, min_periods=window).std()
    lower = mid - num_std * std
    upper = mid + num_std * std

    signal = ctx.new_signal()
    signal[close <= lower] = 1
    signal[close >= upper] = 0
    return signal.ffill().fillna(0)
"""


KDJ_SIGNAL_CODE = """def generate_signals(data, ctx):
    n = int(ctx.params.get("n", 9))
    m1 = int(ctx.params.get("m1", 3))
    m2 = int(ctx.params.get("m2", 3))

    high = data["high"]
    low = data["low"]
    close = data["close"]

    lowest_low = low.rolling(window=n, min_periods=n).min()
    highest_high = high.rolling(window=n, min_periods=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low).replace(0, None) * 100
    k = rsv.ewm(alpha=1/m1, min_periods=n, adjust=False).mean()
    d = k.ewm(alpha=1/m2, min_periods=n, adjust=False).mean()

    signal = ctx.new_signal()
    signal[ctx.cross_over(k, d)] = 1
    signal[ctx.cross_under(k, d)] = 0
    return signal.ffill().fillna(0)
"""


VOLUME_PRICE_DIVERGENCE_CODE = """def generate_signals(data, ctx):
    price_window = int(ctx.params.get("price_window", 20))
    volume_window = int(ctx.params.get("volume_window", 10))
    divergence_threshold = float(ctx.params.get("divergence_threshold", 0.05))

    close = data["close"]
    volume = data["volume"]

    price_ma = ctx.sma(close, price_window)
    volume_ma = ctx.sma(volume, volume_window)

    price_rising = close > price_ma * (1 + divergence_threshold)
    volume_declining = volume < volume_ma * 0.8
    bullish_divergence = price_rising & volume_declining

    price_falling = close < price_ma * (1 - divergence_threshold)
    volume_rising = volume > volume_ma * 1.2
    bearish_divergence = price_falling & volume_rising

    signal = ctx.new_signal()
    signal[bullish_divergence] = 1
    signal[bearish_divergence] = 0
    return signal.ffill().fillna(0)
"""


PRESETS: dict[str, StrategyPreset] = {
    "ma_cross": StrategyPreset(
        id="ma_cross",
        label="双均线策略",
        description="使用快慢均线交叉验证趋势启动与结束区间。",
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
        description="在 RSI 超卖区间尝试买入，在超买区间逐步离场。",
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
        description="突破近期通道高点时入场，跌破通道低点时离场。",
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
        label="事件主题动量验证",
        description="用突破与放量确认事件驱动主题是否具备延续性。",
        summary="结合价格突破与成交量放大，验证资讯主题是否形成持续跟随行情。",
        use_case="适合接在市场资讯预测之后，对候选个股或主题做二次验证与回测交接。",
        risk_notes="事件催化退潮后回撤可能很快放大，需结合回撤、换手和交易成本一起判断。",
        code=EVENT_THEME_MOMENTUM_CODE,
        default_params={
            "lookback_window": 20,
            "volume_window": 5,
            "volume_multiplier": 1.2,
        },
        parameter_schema=[
            {
                "name": "lookback_window",
                "label": "突破回看窗口",
                "type": "number",
                "group": "event",
                "helpText": "窗口越大，要求的价格突破确认越强，信号数量通常更少。",
                "default": 20,
                "min": 5,
                "max": 120,
                "step": 1,
            },
            {
                "name": "volume_window",
                "label": "量能观察窗口",
                "type": "number",
                "group": "event",
                "helpText": "用较短滚动窗口判断事件催化下的成交量是否明显抬升。",
                "default": 5,
                "min": 2,
                "max": 30,
                "step": 1,
            },
            {
                "name": "volume_multiplier",
                "label": "放量倍数",
                "type": "number",
                "group": "event",
                "helpText": "当前成交量需达到滚动均量的该倍数以上才视为有效放量。",
                "default": 1.2,
                "min": 1,
                "max": 5,
                "step": 0.1,
            },
        ],
    ),
    "macd_trend": StrategyPreset(
        id="macd_trend",
        label="MACD 趋势策略",
        description="利用 MACD 快慢线交叉捕捉中短期趋势转折。",
        summary="通过 MACD 线与信号线交叉确认趋势方向。",
        use_case="适合需要过滤震荡噪音、关注趋势延续性的日线级别回测。",
        risk_notes="滞后性较强，趋势末段信号可能出现延迟，建议结合止损使用。",
        code=MACD_TREND_CODE,
        default_params={"fast_period": 12, "slow_period": 26, "signal_period": 9},
        parameter_schema=[
            {
                "name": "fast_period",
                "label": "快线周期",
                "type": "number",
                "group": "trend",
                "helpText": "MACD 快线的 EMA 周期，越短越敏感。",
                "default": 12,
                "min": 2,
                "max": 60,
                "step": 1,
            },
            {
                "name": "slow_period",
                "label": "慢线周期",
                "type": "number",
                "group": "trend",
                "helpText": "MACD 慢线的 EMA 周期，越长越平滑。",
                "default": 26,
                "min": 10,
                "max": 120,
                "step": 1,
            },
            {
                "name": "signal_period",
                "label": "信号线周期",
                "type": "number",
                "group": "trend",
                "helpText": "信号线的 EMA 周期，用于平滑 MACD 线。",
                "default": 9,
                "min": 2,
                "max": 60,
                "step": 1,
            },
        ],
    ),
    "bollinger_reversion": StrategyPreset(
        id="bollinger_reversion",
        label="布林带回归策略",
        description="价格触及布林带下轨时买入，触及上轨时离场。",
        summary="利用布林带上下轨判断超买超卖，做均值回归。",
        use_case="适合震荡行情中寻找价格偏离均值后的回归机会。",
        risk_notes="单边趋势中可能反复触发错误信号，需结合趋势过滤器使用。",
        code=BOLLINGER_REVERSION_CODE,
        default_params={"window": 20, "num_std": 2.0},
        parameter_schema=[
            {
                "name": "window",
                "label": "均线窗口",
                "type": "number",
                "group": "reversion",
                "helpText": "计算中轨的 SMA 窗口，越大越平滑。",
                "default": 20,
                "min": 5,
                "max": 120,
                "step": 1,
            },
            {
                "name": "num_std",
                "label": "标准差倍数",
                "type": "number",
                "group": "reversion",
                "helpText": "布林带宽度由标准差倍数决定，越大通道越宽。",
                "default": 2.0,
                "min": 0.5,
                "max": 5.0,
                "step": 0.1,
            },
        ],
    ),
    "kdj_signal": StrategyPreset(
        id="kdj_signal",
        label="KDJ 信号策略",
        description="利用 KDJ 指标中 K 线与 D 线交叉生成买卖信号。",
        summary="K 线上穿 D 线买入，下穿 D 线卖出。",
        use_case="适合短线或波段交易中寻找动量转折点。",
        risk_notes="KDJ 在极端行情中可能频繁交叉，建议搭配过滤条件或止损使用。",
        code=KDJ_SIGNAL_CODE,
        default_params={"n": 9, "m1": 3, "m2": 3},
        parameter_schema=[
            {
                "name": "n",
                "label": "RSV 窗口",
                "type": "number",
                "group": "momentum",
                "helpText": "计算 RSV 的周期，默认 9 日。",
                "default": 9,
                "min": 3,
                "max": 60,
                "step": 1,
            },
            {
                "name": "m1",
                "label": "K 线平滑",
                "type": "number",
                "group": "momentum",
                "helpText": "K 线的 EWM 平滑参数，越小越平滑。",
                "default": 3,
                "min": 1,
                "max": 20,
                "step": 1,
            },
            {
                "name": "m2",
                "label": "D 线平滑",
                "type": "number",
                "group": "momentum",
                "helpText": "D 线的 EWM 平滑参数，越小越平滑。",
                "default": 3,
                "min": 1,
                "max": 20,
                "step": 1,
            },
        ],
    ),
    "volume_price_divergence": StrategyPreset(
        id="volume_price_divergence",
        label="量价背离策略",
        description="当价格与成交量出现背离时发出交易信号。",
        summary="价涨量缩买入，价跌量增卖出，捕捉量价背离机会。",
        use_case="适合观察资金流向变化、判断趋势是否健康的场景。",
        risk_notes="背离信号可能出现较早，趋势可能延续一段时间后才反转，需配合止损。",
        code=VOLUME_PRICE_DIVERGENCE_CODE,
        default_params={"price_window": 20, "volume_window": 10, "divergence_threshold": 0.05},
        parameter_schema=[
            {
                "name": "price_window",
                "label": "价格均线窗口",
                "type": "number",
                "group": "volume",
                "helpText": "用于判断价格偏离的 SMA 窗口。",
                "default": 20,
                "min": 5,
                "max": 120,
                "step": 1,
            },
            {
                "name": "volume_window",
                "label": "成交量均线窗口",
                "type": "number",
                "group": "volume",
                "helpText": "用于判断成交量变化的 SMA 窗口。",
                "default": 10,
                "min": 2,
                "max": 60,
                "step": 1,
            },
            {
                "name": "divergence_threshold",
                "label": "偏离阈值",
                "type": "number",
                "group": "volume",
                "helpText": "价格偏离均线的比例阈值，越大信号越少但更可靠。",
                "default": 0.05,
                "min": 0.01,
                "max": 0.2,
                "step": 0.01,
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
