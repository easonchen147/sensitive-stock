from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import akquant
import numpy as np
import pandas as pd

from backtesting.data import HistoricalDataRequest, SmartDataProvider
from backtesting.presets import (
    list_strategy_presets,
    resolve_strategy_source,
    serialize_strategy_preset,
)
from backtesting.strategy import StrategyExecutor

DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_ENGINE_NAME = "akquant"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_local_index(index: pd.Index) -> pd.DatetimeIndex:
    datetime_index = pd.DatetimeIndex(pd.to_datetime(index))
    if datetime_index.tz is None:
        return datetime_index.tz_localize(DEFAULT_TIMEZONE)
    return datetime_index.tz_convert(DEFAULT_TIMEZONE)


def _build_fill_policy(execution_mode: str) -> dict[str, Any]:
    if execution_mode == "next_open":
        return {
            "price_basis": "open",
            "bar_offset": 1,
            "temporal": "same_cycle",
        }
    return {
        "price_basis": "close",
        "bar_offset": 0,
        "temporal": "same_cycle",
    }


def _build_slippage_policy(slippage: float) -> dict[str, Any]:
    if slippage <= 0:
        return {"type": "zero"}
    return {"type": "percent", "value": float(slippage)}


def _build_execution_metadata() -> dict[str, Any]:
    return {
        "engine": DEFAULT_ENGINE_NAME,
        "engineVersion": akquant.__version__,
        "runtimeAdapter": "signal_replay",
        "supportedModes": ["close", "next_open"],
        "fillPolicies": [
            {
                "mode": "close",
                "priceBasis": "close",
                "barOffset": 0,
                "temporal": "same_cycle",
            },
            {
                "mode": "next_open",
                "priceBasis": "open",
                "barOffset": 1,
                "temporal": "same_cycle",
            },
        ],
        "supportsRiskControls": True,
    }


def _build_signal_lookup(signal: pd.Series) -> dict[int, float]:
    localized = signal.copy()
    localized.index = _to_local_index(localized.index)
    return {
        int(timestamp.value): float(np.clip(value, 0.0, 1.0))
        for timestamp, value in localized.items()
        if not pd.isna(value)
    }


def _build_pre_open_signal_lookup(signal: pd.Series) -> dict[int, float]:
    localized = signal.copy()
    localized.index = _to_local_index(localized.index)
    previous_signal = 0.0
    lookup: dict[int, float] = {}

    for timestamp, value in localized.items():
        lookup[int(timestamp.normalize().value)] = previous_signal
        if not pd.isna(value):
            previous_signal = float(np.clip(value, 0.0, 1.0))

    return lookup


def _build_akquant_frame(symbol: str, data: pd.DataFrame) -> pd.DataFrame:
    frame = data.reset_index()
    date_column = frame.columns[0]
    frame = frame.rename(columns={date_column: "date"}).copy()
    frame["symbol"] = symbol
    required_columns = ["date", "open", "high", "low", "close", "volume", "symbol"]
    for column in required_columns:
        if column not in frame.columns:
            raise ValueError(f"AKQuant data frame missing required column: {column}")
    return frame[required_columns]


def _metric_value(result: Any, name: str, default: float = 0.0) -> float:
    metrics_df = getattr(result, "metrics_df", None)
    if isinstance(metrics_df, pd.DataFrame) and not metrics_df.empty and name in metrics_df.index:
        value_column = "value" if "value" in metrics_df.columns else metrics_df.columns[0]
        return _safe_float(metrics_df.at[name, value_column], default)

    metrics = getattr(result, "metrics", None)
    if metrics is not None and hasattr(metrics, name):
        return _safe_float(getattr(metrics, name), default)

    return default


def _series_rows(series: pd.Series) -> list[dict[str, Any]]:
    if series.empty:
        return []

    rows: list[dict[str, Any]] = []
    for index, value in series.items():
        if pd.isna(value):
            continue
        rows.append(
            {
                "date": pd.Timestamp(index).tz_convert(DEFAULT_TIMEZONE).strftime("%Y-%m-%d"),
                "value": float(value),
            }
        )
    return rows


def _monthly_rows(series: pd.Series) -> list[dict[str, Any]]:
    if series.empty:
        return []

    rows: list[dict[str, Any]] = []
    for index, value in series.items():
        if pd.isna(value):
            continue
        rows.append(
            {
                "month": pd.Timestamp(index).strftime("%Y-%m"),
                "value": float(value),
            }
        )
    return rows


def _build_benchmark_series(
    *,
    benchmark: pd.DataFrame | None,
    equity: pd.Series,
    initial_capital: float,
) -> tuple[pd.Series, dict[str, float | None]]:
    comparison: dict[str, float | None] = {
        "benchmark_total_return": None,
        "excess_return": None,
        "information_ratio": None,
        "tracking_error": None,
    }
    if benchmark is None or benchmark.empty or "close" not in benchmark.columns or equity.empty:
        return pd.Series(dtype=float), comparison

    close = benchmark["close"].copy()
    close.index = _to_local_index(close.index)
    aligned = close.reindex(equity.index).ffill().bfill()
    if aligned.empty or aligned.isna().all():
        return pd.Series(dtype=float), comparison

    base_price = _safe_float(aligned.iloc[0])
    if base_price <= 0:
        return pd.Series(dtype=float), comparison

    benchmark_equity = aligned / base_price * initial_capital
    benchmark_returns = benchmark_equity.pct_change().fillna(0.0)
    strategy_returns = equity.pct_change().fillna(0.0)
    excess_returns = strategy_returns - benchmark_returns
    std = float(excess_returns.std()) if len(excess_returns) > 1 else 0.0

    benchmark_total_return = float(benchmark_equity.iloc[-1] / initial_capital - 1)
    strategy_total_return = float(equity.iloc[-1] / initial_capital - 1)
    comparison.update(
        {
            "benchmark_total_return": benchmark_total_return,
            "excess_return": strategy_total_return - benchmark_total_return,
            "information_ratio": (
                float(excess_returns.mean() / std * np.sqrt(252)) if std > 0 else 0.0
            ),
            "tracking_error": float(std * np.sqrt(252)) if std > 0 else 0.0,
        }
    )
    return benchmark_equity, comparison


def _build_assumptions(settings: dict[str, Any]) -> list[dict[str, str]]:
    fill_policy = settings.get("fillPolicy") or {}
    execution_mode = str(settings.get("executionMode") or "close")
    if execution_mode == "next_open":
        execution_detail = (
            "使用 AKQuant pre-open same_cycle/open fill policy。上一交易日收盘确认的信号，"
            "会在下一交易日开盘前提交并按当日开盘价执行。"
        )
    else:
        execution_detail = "使用 AKQuant same_cycle/close fill policy。信号在当前 bar 收盘价执行。"

    stop_loss = float(settings.get("stopLoss") or 0.0)
    take_profit = float(settings.get("takeProfit") or 0.0)
    risk_value = (
        f"止损 {stop_loss * 100:.1f}% / 止盈 {take_profit * 100:.1f}%"
        if stop_loss > 0 or take_profit > 0
        else "止损 关闭 / 止盈 关闭"
    )

    return [
        {
            "label": "回测内核",
            "value": (
                f"{settings.get('engine', DEFAULT_ENGINE_NAME)} "
                f"{settings.get('engineVersion', '')}"
            ).strip(),
            "detail": (
                "使用官方 AKQuant runtime 执行回测，"
                "旧 backtesting.engine 已降级为兼容辅助层。"
            ),
        },
        {
            "label": "执行模式",
            "value": execution_mode,
            "detail": execution_detail,
        },
        {
            "label": "成交规则",
            "value": (
                f"{fill_policy.get('priceBasis', 'close')} / "
                f"offset {fill_policy.get('barOffset', 0)} / "
                f"{fill_policy.get('temporal', 'same_cycle')}"
            ),
            "detail": "返回的是 AKQuant 最终采用的 fill policy，而不是前端本地推断。",
        },
        {
            "label": "仓位与手数",
            "value": (
                f"仓位 {float(settings.get('positionSize') or 0.0) * 100:.0f}% / "
                f"手数 {int(settings.get('lotSize') or 0)}"
            ),
            "detail": "订单按 A 股整手约束下发，现金不足时会收缩到可成交数量而不是直接失败。",
        },
        {
            "label": "交易成本",
            "value": (
                f"佣金 {float(settings.get('tradingFee') or 0.0) * 100:.2f}% / "
                f"印花税 {float(settings.get('stampTax') or 0.0) * 100:.2f}% / "
                f"滑点 {float(settings.get('slippage') or 0.0) * 100:.2f}%"
            ),
            "detail": "费用通过 AKQuant 佣金/税费/滑点参数生效，卖出税费会体现在成交成本里。",
        },
        {
            "label": "风险控制",
            "value": risk_value,
            "detail": (
                "止损止盈通过 AKQuant 保护性卖单建模。若保护单在场，信号平仓会先撤保护单，"
                "再在下一可成交周期离场。"
            ),
        },
    ]


def _build_insights(
    *,
    metrics: dict[str, Any],
    comparison: dict[str, Any],
    trade_stats: dict[str, Any],
    warnings: list[str],
) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []

    excess_return = comparison.get("excess_return")
    benchmark_return = comparison.get("benchmark_total_return")
    if benchmark_return is not None and excess_return is not None:
        tone = "positive" if float(excess_return) >= 0 else "warning"
        direction = "跑赢" if float(excess_return) >= 0 else "跑输"
        insights.append(
            {
                "title": "相对基准",
                "tone": tone,
                "detail": (
                    f"策略{direction}基准 {abs(float(excess_return)) * 100:.2f}%，"
                    f"基准收益 {float(benchmark_return) * 100:.2f}%。"
                ),
            }
        )

    max_drawdown = float(metrics.get("max_drawdown") or 0.0)
    annualized = float(metrics.get("annualized_return") or 0.0)
    insights.append(
        {
            "title": "回撤画像",
            "tone": "positive" if abs(max_drawdown) <= 0.1 else "warning",
            "detail": (
                f"最大回撤 {abs(max_drawdown) * 100:.2f}%，"
                f"年化收益 {annualized * 100:.2f}%。"
            ),
        }
    )
    insights.append(
        {
            "title": "交易执行",
            "tone": "neutral",
            "detail": (
                f"共 {int(trade_stats.get('tradeCount') or 0)} 笔成交，"
                f"暴露率 {float(trade_stats.get('exposureRate') or 0.0) * 100:.2f}%，"
                f"总成本 {float(trade_stats.get('totalCosts') or 0.0):.2f}。"
            ),
        }
    )

    if warnings:
        insights.append(
            {
                "title": "执行告警",
                "tone": "warning",
                "detail": " / ".join(warnings[:2]),
            }
        )

    return insights


def _serialize_orders(
    *,
    orders_df: pd.DataFrame,
    stamp_tax_rate: float,
    protective_levels: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    if orders_df.empty:
        return []

    filled = orders_df.copy()
    filled["status_lower"] = filled["status"].astype(str).str.lower()
    filled = filled[filled["status_lower"] == "filled"]
    if filled.empty:
        return []

    records: list[dict[str, Any]] = []
    for _, row in filled.iterrows():
        quantity = int(_safe_float(row.get("filled_quantity") or row.get("quantity")))
        price = _safe_float(row.get("avg_price"))
        notional = float(price * quantity)
        action = str(row.get("side") or "").capitalize()
        is_sell = action == "Sell"
        reason = str(row.get("tag") or "")
        if is_sell and reason == "signal_change" and protective_levels:
            symbol_key = str(row.get("symbol") or "")
            symbol_levels = protective_levels.get(symbol_key)
            if symbol_levels is None and len(protective_levels) == 1:
                symbol_levels = next(iter(protective_levels.values()))
            for level in symbol_levels or []:
                level_price = _safe_float(level.get("price"))
                if level_price > 0 and np.isclose(price, level_price):
                    reason = str(level.get("reason") or reason)
                    break
        tax = float(notional * stamp_tax_rate) if is_sell else 0.0
        commission_total = _safe_float(row.get("commission"))
        fee = max(0.0, commission_total - tax)
        updated_at = pd.Timestamp(row.get("updated_at"))
        records.append(
            {
                "date": updated_at.tz_convert(DEFAULT_TIMEZONE).strftime("%Y-%m-%d"),
                "action": action,
                "reason": reason,
                "price": price,
                "shares": quantity,
                "notional": notional,
                "fee": fee,
                "tax": tax,
            }
        )
    return records


def serialize_symbol_result(
    symbol: str,
    result: Any,
    *,
    settings: dict[str, Any],
    benchmark: pd.DataFrame | None = None,
    warnings: list[str] | None = None,
    protective_levels: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    normalized_warnings = list(warnings or [])
    equity_curve = getattr(result, "equity_curve_daily", pd.Series(dtype=float)).copy()
    if equity_curve.empty:
        equity_curve = getattr(result, "equity_curve", pd.Series(dtype=float)).copy()
    if equity_curve.empty:
        raise ValueError(f"{symbol} 回测结果缺少权益曲线")

    equity_curve.index = _to_local_index(equity_curve.index)
    cash_curve = getattr(result, "cash_curve_daily", pd.Series(dtype=float)).copy()
    if cash_curve.empty:
        cash_curve = getattr(result, "cash_curve", pd.Series(dtype=float)).copy()
    if cash_curve.empty:
        cash_curve = pd.Series(settings["initialCapital"], index=equity_curve.index, dtype=float)
    else:
        cash_curve.index = _to_local_index(cash_curve.index)
        cash_curve = (
            cash_curve.reindex(equity_curve.index)
            .ffill()
            .fillna(settings["initialCapital"])
        )

    market_value = (equity_curve - cash_curve).clip(lower=0.0)
    position_curve = (
        market_value / equity_curve.replace(0.0, np.nan)
    ).fillna(0.0)
    drawdown_curve = equity_curve / equity_curve.cummax() - 1
    monthly_returns = equity_curve.resample("ME").last().pct_change().dropna()

    benchmark_curve, comparison = _build_benchmark_series(
        benchmark=benchmark,
        equity=equity_curve,
        initial_capital=float(settings["initialCapital"]),
    )

    metrics = {
        "strategy_total_return": _metric_value(result, "total_return_pct") / 100.0,
        "annualized_return": _metric_value(result, "annualized_return") / 100.0,
        "volatility": _metric_value(result, "volatility") / 100.0,
        "sharpe": _metric_value(result, "sharpe_ratio"),
        "max_drawdown": -abs(_metric_value(result, "max_drawdown_pct") / 100.0),
        "win_rate": _metric_value(result, "win_rate") / 100.0,
        "trading_days": float(len(equity_curve)),
        "profit_factor": _metric_value(result, "profit_factor"),
    }

    orders_df = getattr(result, "orders_df", pd.DataFrame())
    if not isinstance(orders_df, pd.DataFrame):
        orders_df = pd.DataFrame()
    trades_df = getattr(result, "trades_df", pd.DataFrame())
    if not isinstance(trades_df, pd.DataFrame):
        trades_df = pd.DataFrame()

    if not orders_df.empty:
        rejected = orders_df[orders_df["status"].astype(str).str.lower() == "rejected"]
        for _, row in rejected.head(3).iterrows():
            reason = str(row.get("reject_reason") or "未知原因")
            normalized_warnings.append(f"{symbol} 订单被拒绝: {reason}")

    trade_records = _serialize_orders(
        orders_df=orders_df,
        stamp_tax_rate=float(settings.get("stampTax") or 0.0),
        protective_levels=protective_levels,
    )
    trade_costs = float(sum(item["fee"] + item["tax"] for item in trade_records))
    turnover = (
        float(sum(item["notional"] for item in trade_records) / float(settings["initialCapital"]))
        if trade_records
        else 0.0
    )
    exposure_rate = (
        float((position_curve > 0).sum() / len(position_curve))
        if len(position_curve)
        else 0.0
    )
    ending_equity = float(equity_curve.iloc[-1])
    net_profit = float(ending_equity - float(settings["initialCapital"]))

    duration_series = pd.Series(dtype=float)
    if not trades_df.empty and "duration" in trades_df.columns:
        if pd.api.types.is_timedelta64_dtype(trades_df["duration"]):
            duration_series = pd.to_numeric(
                trades_df["duration"].dt.total_seconds() / (24 * 3600),
                errors="coerce",
            )
        else:
            duration_series = pd.to_numeric(trades_df["duration"], errors="coerce")

    average_holding_days = (
        float(duration_series.mean()) if not duration_series.empty else 0.0
    )
    average_trade_return = (
        float(pd.to_numeric(trades_df["return_pct"], errors="coerce").fillna(0.0).mean() / 100.0)
        if not trades_df.empty and "return_pct" in trades_df.columns
        else 0.0
    )
    closed_trade_win_rate = (
        float(
            (
                pd.to_numeric(trades_df["net_pnl"], errors="coerce").fillna(0.0) > 0
            ).mean()
        )
        if not trades_df.empty and "net_pnl" in trades_df.columns
        else 0.0
    )

    trade_stats = {
        "tradeCount": len(trade_records),
        "winRate": closed_trade_win_rate,
        "averageHoldingDays": average_holding_days,
        "averageTradeReturn": average_trade_return,
        "totalCosts": trade_costs,
        "turnover": turnover,
        "endingEquity": ending_equity,
        "netProfit": net_profit,
        "exposureRate": exposure_rate,
    }

    if not trade_records:
        normalized_warnings.append("本次回测未产生成交记录。")

    assumptions = _build_assumptions(settings)
    insights = _build_insights(
        metrics=metrics,
        comparison=comparison,
        trade_stats=trade_stats,
        warnings=normalized_warnings,
    )

    return {
        "symbol": symbol,
        "settings": settings,
        "metrics": metrics,
        "comparison": comparison,
        "series": {
            "equity": _series_rows(equity_curve),
            "benchmark": _series_rows(benchmark_curve),
            "drawdown": _series_rows(drawdown_curve),
            "position": _series_rows(position_curve),
            "cash": _series_rows(cash_curve),
            "monthlyReturns": _monthly_rows(monthly_returns),
        },
        "tradeStats": trade_stats,
        "trades": trade_records,
        "warnings": normalized_warnings,
        "assumptions": assumptions,
        "insights": insights,
    }


class SignalReplayStrategy(akquant.Strategy):
    def __init__(
        self,
        *,
        primary_symbol: str,
        execution_mode: str,
        signal_lookup: dict[int, float],
        pre_open_signal_lookup: dict[int, float],
        position_size: float,
        stop_loss: float,
        take_profit: float,
    ) -> None:
        super().__init__()
        self.primary_symbol = primary_symbol
        self.execution_mode = execution_mode
        self.signal_lookup = signal_lookup
        self.pre_open_signal_lookup = pre_open_signal_lookup
        self.position_size = float(max(0.0, min(1.0, position_size)))
        self.stop_loss = float(max(0.0, stop_loss))
        self.take_profit = float(max(0.0, take_profit))
        self.protective_levels: dict[str, dict[str, float]] = {}
        self.closed_protective_levels: dict[str, list[dict[str, Any]]] = {}

    def _signal_key(self, timestamp_ns: int) -> int:
        return int(
            pd.Timestamp(timestamp_ns, unit="ns", tz="UTC")
            .tz_convert(DEFAULT_TIMEZONE)
            .normalize()
            .value
        )

    def _trading_day_key(self, value: Any) -> int:
        timestamp = pd.Timestamp(value)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize(DEFAULT_TIMEZONE)
        else:
            timestamp = timestamp.tz_convert(DEFAULT_TIMEZONE)
        return int(timestamp.normalize().value)

    def _target_percent(self, raw_signal: float) -> float:
        return float(np.clip(raw_signal, 0.0, 1.0)) * self.position_size

    def _arm_protective_orders(self, symbol: str) -> None:
        if self.stop_loss <= 0 and self.take_profit <= 0:
            return

        levels = self.protective_levels.get(symbol)
        if not levels:
            return

        available_position = float(self.get_available_position(symbol))
        if available_position <= 0:
            return

        if list(self.get_open_orders(symbol)):
            return

        stop_order_id = ""
        take_order_id = ""
        if "stop_loss" in levels:
            stop_order_id = self.sell(
                symbol=symbol,
                quantity=available_position,
                trigger_price=float(levels["stop_loss"]),
                tag="stop_loss",
            )
        if "take_profit" in levels:
            take_order_id = self.sell(
                symbol=symbol,
                quantity=available_position,
                price=float(levels["take_profit"]),
                tag="take_profit",
            )
        if stop_order_id and take_order_id:
            self.create_oco_order_group(stop_order_id, take_order_id)

    def _protective_will_trigger(self, symbol: str, bar: Any) -> bool:
        levels = self.protective_levels.get(symbol)
        if not levels:
            return False

        low_price = _safe_float(bar.low)
        high_price = _safe_float(bar.high)
        stop_price = levels.get("stop_loss")
        take_price = levels.get("take_profit")
        if stop_price is not None and low_price > 0 and low_price <= stop_price:
            return True
        if take_price is not None and high_price > 0 and high_price >= take_price:
            return True
        return False

    def _flatten_position(self, symbol: str, *, tag: str) -> None:
        available_position = float(self.get_available_position(symbol))
        if available_position <= 0:
            return

        if list(self.get_open_orders(symbol)):
            self.cancel_all_orders(symbol)

        self.sell(symbol=symbol, quantity=available_position, tag=tag)

    def _submit_entry(self, symbol: str, *, target_percent: float) -> None:
        if target_percent <= 0 or list(self.get_open_orders(symbol)):
            return
        self.order_target_percent(target_percent, symbol=symbol, tag="signal_change")

    def _handle_target(self, *, symbol: str, target_percent: float, bar: Any | None = None) -> None:
        current_position = float(self.get_position(symbol))
        available_position = float(self.get_available_position(symbol))
        open_orders = list(self.get_open_orders(symbol))

        if current_position <= 0:
            self._submit_entry(symbol, target_percent=target_percent)
            return

        if target_percent <= 0:
            if bar is not None and open_orders and self._protective_will_trigger(symbol, bar):
                return
            if available_position <= 0:
                return
            self._flatten_position(symbol, tag="signal_change")
            return

        self._arm_protective_orders(symbol)

    def on_pre_open(self, event: dict[str, Any]) -> None:
        if self.execution_mode != "next_open":
            return

        target_percent = self._target_percent(
            self.pre_open_signal_lookup.get(self._trading_day_key(event["trading_date"]), 0.0)
        )
        self._handle_target(symbol=self.primary_symbol, target_percent=target_percent)

    def on_bar(self, bar: Any) -> None:
        symbol = str(bar.symbol)
        signal_lookup = self.signal_lookup
        signal_key = self._signal_key(int(bar.timestamp))
        if self.execution_mode == "next_open":
            signal_lookup = self.pre_open_signal_lookup
            signal_key = self._trading_day_key(pd.Timestamp(bar.timestamp, unit="ns", tz="UTC"))

        target_percent = self._target_percent(signal_lookup.get(signal_key, 0.0))
        self._handle_target(symbol=symbol, target_percent=target_percent, bar=bar)

    def on_trade(self, trade: Any) -> None:
        symbol = str(trade.symbol)
        side = str(trade.side)
        if side == "OrderSide.Buy":
            entry_price = _safe_float(trade.price)
            if self.stop_loss > 0 or self.take_profit > 0:
                stop_level = (
                    entry_price * (1 - self.stop_loss) if self.stop_loss > 0 else None
                )
                take_level = (
                    entry_price * (1 + self.take_profit) if self.take_profit > 0 else None
                )
                self.protective_levels[symbol] = {
                    key: value
                    for key, value in {"stop_loss": stop_level, "take_profit": take_level}.items()
                    if value is not None
                }
        elif side == "OrderSide.Sell" and float(self.get_position(symbol)) <= 0:
            closing_price = _safe_float(trade.price)
            for reason, level_price in self.protective_levels.get(symbol, {}).items():
                if closing_price > 0 and np.isclose(closing_price, level_price):
                    self.closed_protective_levels.setdefault(symbol, []).append(
                        {"reason": reason, "price": level_price}
                    )
                    break
            else:
                take_profit_price = self.protective_levels.get(symbol, {}).get("take_profit")
                if (
                    take_profit_price is not None
                    and closing_price > float(take_profit_price) * 0.98
                ):
                    self.closed_protective_levels.setdefault(symbol, []).append(
                        {"reason": "take_profit", "price": closing_price}
                    )
                stop_loss_price = self.protective_levels.get(symbol, {}).get("stop_loss")
                if stop_loss_price is not None and closing_price < float(stop_loss_price) * 1.02:
                    self.closed_protective_levels.setdefault(symbol, []).append(
                        {"reason": "stop_loss", "price": closing_price}
                    )
            self.protective_levels.pop(symbol, None)

    def on_order(self, order: Any) -> None:
        status = str(getattr(order, "status", ""))
        side = str(getattr(order, "side", ""))
        reason = str(getattr(order, "tag", "") or "")
        if status != "OrderStatus.Filled" or side != "OrderSide.Sell":
            return
        if reason not in {"stop_loss", "take_profit"}:
            return

        symbol = str(getattr(order, "symbol", "") or self.primary_symbol)
        price = _safe_float(getattr(order, "avg_price", None) or getattr(order, "price", None))
        self.closed_protective_levels.setdefault(symbol, []).append(
            {"reason": reason, "price": price}
        )


@dataclass
class AKQuantBacktestService:
    market_data_provider_factory: Callable[[], Any] = SmartDataProvider
    strategy_executor: StrategyExecutor = field(default_factory=StrategyExecutor)
    runtime_runner: Callable[..., Any] = akquant.run_backtest

    def list_presets(self) -> dict[str, list[dict[str, Any]]]:
        items: list[dict[str, Any]] = []
        execution_metadata = _build_execution_metadata()
        for preset in list_strategy_presets():
            payload = serialize_strategy_preset(preset)
            payload["executionMetadata"] = dict(execution_metadata)
            items.append(payload)
        return {"items": items}

    def run_batch(self, request: Any) -> dict[str, list[dict[str, Any]]]:
        provider = self.market_data_provider_factory()
        results: list[dict[str, Any]] = []
        failures: list[dict[str, str]] = []

        for symbol in request.symbols:
            try:
                results.append(self._run_symbol(provider=provider, request=request, symbol=symbol))
            except Exception as exc:
                failures.append({"symbol": symbol, "message": str(exc)})

        return {"results": results, "failures": failures}

    def _run_symbol(self, *, provider: Any, request: Any, symbol: str) -> dict[str, Any]:
        warnings: list[str] = []
        resolved_code, preset = resolve_strategy_source(
            mode=request.strategy_mode,
            preset_id=request.strategy_preset,
            custom_code=request.strategy_code,
        )
        data = provider.get_ohlcv(
            HistoricalDataRequest(
                symbol=symbol,
                start_date=request.start_date.isoformat(),
                end_date=request.end_date.isoformat(),
                adjust=request.adjust,
            )
        )
        benchmark = self._load_benchmark(provider=provider, request=request, warnings=warnings)
        signal = self.strategy_executor.execute(resolved_code, data, request.params)
        signal_lookup = _build_signal_lookup(signal)
        pre_open_signal_lookup = _build_pre_open_signal_lookup(signal)

        if request.execution_mode == "next_open" and len(signal) >= 2:
            if not np.isclose(float(signal.iloc[-1]), float(signal.iloc[-2])):
                warnings.append(
                    "next_open 模式下最后一个信号变化缺少下一次成交事件，"
                    "最终调仓可能不会成交。"
                )

        fill_policy = _build_fill_policy(request.execution_mode)
        strategy = SignalReplayStrategy(
            primary_symbol=symbol,
            execution_mode=request.execution_mode,
            signal_lookup=signal_lookup,
            pre_open_signal_lookup=pre_open_signal_lookup,
            position_size=request.position_size,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
        )
        runtime_result = self.runtime_runner(
            data=_build_akquant_frame(symbol, data),
            strategy=strategy,
            symbols=symbol,
            initial_cash=request.initial_capital,
            commission_rate=request.trading_fee,
            stamp_tax_rate=request.stamp_tax,
            slippage=_build_slippage_policy(request.slippage),
            lot_size=request.lot_size,
            fill_policy=fill_policy,
            t_plus_one=True,
            show_progress=False,
        )
        source_details = (
            provider.describe_sources() if hasattr(provider, "describe_sources") else {}
        )
        settings = {
            "symbol": symbol,
            "initialCapital": request.initial_capital,
            "benchmarkSymbol": request.benchmark_symbol,
            "adjust": request.adjust,
            "strategyMode": request.strategy_mode,
            "strategyPreset": request.strategy_preset,
            "strategyLabel": preset.label if preset else "自定义策略",
            "executionMode": request.execution_mode,
            "positionSize": request.position_size,
            "lotSize": request.lot_size,
            "tradingFee": request.trading_fee,
            "stampTax": request.stamp_tax,
            "slippage": request.slippage,
            "stopLoss": request.stop_loss,
            "takeProfit": request.take_profit,
            "engine": DEFAULT_ENGINE_NAME,
            "engineVersion": akquant.__version__,
            "fillPolicy": {
                "priceBasis": fill_policy["price_basis"],
                "barOffset": fill_policy["bar_offset"],
                "temporal": fill_policy["temporal"],
            },
            **source_details,
        }
        return serialize_symbol_result(
            symbol,
            runtime_result,
            settings=settings,
            benchmark=benchmark,
            warnings=warnings,
            protective_levels=strategy.closed_protective_levels,
        )

    def _load_benchmark(
        self,
        *,
        provider: Any,
        request: Any,
        warnings: list[str],
    ) -> pd.DataFrame | None:
        benchmark_symbol = request.benchmark_symbol
        if not benchmark_symbol:
            return None

        try:
            return provider.get_ohlcv(
                HistoricalDataRequest(
                    symbol=benchmark_symbol,
                    start_date=request.start_date.isoformat(),
                    end_date=request.end_date.isoformat(),
                    adjust=request.adjust,
                )
            )
        except Exception as exc:
            warnings.append(f"基准 {benchmark_symbol} 获取失败，已跳过对比: {exc}")
            return None
