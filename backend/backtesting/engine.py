from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


def _max_drawdown(equity: pd.Series) -> float:
    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    return float(drawdown.min()) if not drawdown.empty else 0.0


def _annualize_from_returns(returns: pd.Series) -> float:
    periods = len(returns)
    if periods <= 1:
        return 0.0
    total_return = (1 + returns.fillna(0)).prod() - 1
    return float((1 + total_return) ** (252 / periods) - 1)


def _safe_float(value: Any) -> float:
    return float(value) if value is not None else 0.0


def _round_lot(shares: float, lot_size: int) -> int:
    if shares <= 0:
        return 0
    return int(shares // lot_size * lot_size)


@dataclass
class BacktestResult:
    performance: pd.DataFrame
    metrics: dict[str, float]
    signal: pd.Series
    trades: pd.DataFrame
    settings: dict[str, Any] = field(default_factory=dict)
    comparison: dict[str, float | None] = field(default_factory=dict)
    trade_stats: dict[str, float | int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    monthly_returns: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))


@dataclass
class Backtester:
    initial_capital: float = 100000.0
    trading_fee: float = 0.0005
    stamp_tax: float = 0.001
    slippage: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    execution_mode: str = "close"
    position_size: float = 1.0
    lot_size: int = 100

    def run(
        self,
        data: pd.DataFrame,
        signal: pd.Series,
        benchmark: pd.DataFrame | None = None,
        settings: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
    ) -> BacktestResult:
        signal = signal.reindex(data.index).ffill().fillna(0.0).astype(float)
        result_warnings = list(warnings or [])

        if self.execution_mode not in {"close", "next_open"}:
            raise ValueError(f"不支持的 execution_mode: {self.execution_mode}")

        clipped_signal = signal.clip(lower=0.0, upper=1.0)
        if not clipped_signal.equals(signal):
            result_warnings.append("检测到超出 A 股 long-only 范围的信号，已裁剪到 0~1。")
        signal = clipped_signal

        cash = float(self.initial_capital)
        shares = 0
        entry_price: float | None = None
        entry_date: pd.Timestamp | None = None
        pending_signal: float | None = None
        round_trips: list[dict[str, float]] = []
        rows: list[dict[str, Any]] = []
        trades: list[dict[str, Any]] = []

        def record_trade(
            *,
            date: pd.Timestamp,
            action: str,
            reason: str,
            price: float,
            trade_shares: int,
            fee: float,
            tax: float,
        ) -> None:
            trades.append(
                {
                    "date": date,
                    "action": action,
                    "reason": reason,
                    "price": price,
                    "shares": int(trade_shares),
                    "notional": float(price * trade_shares),
                    "fee": float(fee),
                    "tax": float(tax),
                }
            )

        def trade_to_target(
            *,
            target_signal: float,
            date: pd.Timestamp,
            reference_price: float,
            reason: str,
        ) -> None:
            nonlocal cash, shares, entry_price, entry_date

            total_equity = cash + shares * reference_price
            target_weight = float(max(0.0, min(1.0, target_signal))) * float(
                max(0.0, min(1.0, self.position_size))
            )
            target_shares = _round_lot(
                (total_equity * target_weight) / reference_price,
                self.lot_size,
            )

            if target_shares == shares:
                return

            if target_shares > shares:
                buy_shares = target_shares - shares
                exec_price = reference_price * (1 + self.slippage)
                max_affordable = _round_lot(
                    cash / (exec_price * (1 + self.trading_fee)),
                    self.lot_size,
                )
                buy_shares = min(buy_shares, max_affordable)
                if buy_shares <= 0:
                    result_warnings.append(f"{date.strftime('%Y-%m-%d')} 现金不足，未能完成买入。")
                    return

                notional = exec_price * buy_shares
                fee = notional * self.trading_fee
                cash -= notional + fee
                if cash < 0:
                    cash = 0.0
                previous_shares = shares
                shares += buy_shares
                if previous_shares == 0:
                    entry_price = exec_price
                    entry_date = date
                elif entry_price is not None:
                    entry_price = ((entry_price * previous_shares) + notional) / shares

                record_trade(
                    date=date,
                    action="Buy",
                    reason=reason,
                    price=exec_price,
                    trade_shares=buy_shares,
                    fee=fee,
                    tax=0.0,
                )
                return

            sell_shares = shares - target_shares
            exec_price = reference_price * (1 - self.slippage)
            notional = exec_price * sell_shares
            fee = notional * self.trading_fee
            tax = notional * self.stamp_tax
            cash += notional - fee - tax
            shares -= sell_shares

            if shares == 0 and entry_price is not None and entry_date is not None:
                gross_pnl = (exec_price - entry_price) * sell_shares
                net_pnl = gross_pnl - fee - tax
                holding_days = max((date - entry_date).days, 1)
                round_trips.append(
                    {
                        "return": float((exec_price / entry_price) - 1),
                        "pnl": float(net_pnl),
                        "holding_days": float(holding_days),
                    }
                )
                entry_price = None
                entry_date = None

            record_trade(
                date=date,
                action="Sell",
                reason=reason,
                price=exec_price,
                trade_shares=sell_shares,
                fee=fee,
                tax=tax,
            )

        for index, date in enumerate(data.index):
            row = data.loc[date]
            date = pd.Timestamp(date)
            open_price = _safe_float(row.get("open")) or _safe_float(row.get("close"))
            close_price = _safe_float(row.get("close")) or open_price
            low_price = _safe_float(row.get("low")) or close_price
            high_price = _safe_float(row.get("high")) or close_price
            target_signal = float(signal.iloc[index])
            previous_signal = float(signal.iloc[index - 1]) if index > 0 else 0.0

            if self.execution_mode == "next_open" and pending_signal is not None:
                trade_to_target(
                    target_signal=pending_signal,
                    date=date,
                    reference_price=open_price,
                    reason="signal_change",
                )
                pending_signal = None

            risk_closed = False
            if shares > 0 and entry_price is not None:
                if self.stop_loss > 0 and low_price <= entry_price * (1 - self.stop_loss):
                    trade_to_target(
                        target_signal=0.0,
                        date=date,
                        reference_price=entry_price * (1 - self.stop_loss),
                        reason="stop_loss",
                    )
                    risk_closed = True
                elif self.take_profit > 0 and high_price >= entry_price * (1 + self.take_profit):
                    trade_to_target(
                        target_signal=0.0,
                        date=date,
                        reference_price=entry_price * (1 + self.take_profit),
                        reason="take_profit",
                    )
                    risk_closed = True

            signal_changed = index == 0 or not np.isclose(target_signal, previous_signal)
            if not risk_closed and signal_changed:
                if self.execution_mode == "close":
                    trade_to_target(
                        target_signal=target_signal,
                        date=date,
                        reference_price=close_price,
                        reason="signal_change",
                    )
                elif index < len(data.index) - 1:
                    pending_signal = target_signal
                elif not np.isclose(target_signal, previous_signal):
                    result_warnings.append(
                        "next_open 模式下最后一个信号变化缺少下一根开盘价，已忽略。"
                    )

            market_value = shares * close_price
            strategy_equity = cash + market_value
            rows.append(
                {
                    "date": date,
                    "open": open_price,
                    "close": close_price,
                    "cash": float(cash),
                    "shares": int(shares),
                    "market_value": float(market_value),
                    "strategy_equity": float(strategy_equity),
                    "position": (
                        float(market_value / strategy_equity)
                        if strategy_equity > 0
                        else 0.0
                    ),
                }
            )

        performance = pd.DataFrame(rows).set_index("date")
        performance["strategy_returns"] = performance["strategy_equity"].pct_change().fillna(0.0)
        performance["drawdown"] = (
            performance["strategy_equity"] / performance["strategy_equity"].cummax() - 1
        )

        comparison = self._build_benchmark_comparison(
            performance=performance,
            benchmark=benchmark,
            warnings=result_warnings,
        )

        metrics = self._build_metrics(performance)
        trade_stats = self._build_trade_stats(trades, round_trips)
        monthly_returns = (
            performance["strategy_equity"].resample("ME").last().pct_change().dropna()
            if not performance.empty
            else pd.Series(dtype=float)
        )

        trades_df = pd.DataFrame(trades)
        if not trades_df.empty:
            trades_df["date"] = pd.to_datetime(trades_df["date"])

        if trades_df.empty:
            result_warnings.append("本次回测未产生成交记录。")

        return BacktestResult(
            performance=performance,
            metrics=metrics,
            signal=signal,
            trades=trades_df,
            settings=settings or {},
            comparison=comparison,
            trade_stats=trade_stats,
            warnings=result_warnings,
            monthly_returns=monthly_returns,
        )

    def _build_benchmark_comparison(
        self,
        *,
        performance: pd.DataFrame,
        benchmark: pd.DataFrame | None,
        warnings: list[str],
    ) -> dict[str, float | None]:
        comparison: dict[str, float | None] = {
            "benchmark_total_return": None,
            "excess_return": None,
            "information_ratio": None,
            "tracking_error": None,
        }
        if benchmark is None or benchmark.empty or "close" not in benchmark.columns:
            return comparison

        aligned = benchmark.reindex(performance.index).copy()
        aligned["close"] = aligned["close"].ffill().bfill()
        if aligned["close"].isna().all():
            warnings.append("基准数据无法对齐，已跳过基准比较。")
            return comparison

        base_price = float(aligned["close"].iloc[0])
        if base_price <= 0:
            warnings.append("基准初始价格无效，已跳过基准比较。")
            return comparison

        performance["bench_equity"] = aligned["close"] / base_price * self.initial_capital
        performance["benchmark_returns"] = performance["bench_equity"].pct_change().fillna(0.0)

        benchmark_total_return = (
            performance["bench_equity"].iloc[-1] / self.initial_capital - 1
            if not performance.empty
            else 0.0
        )
        excess_returns = performance["strategy_returns"] - performance["benchmark_returns"]
        tracking_error = (
            float(excess_returns.std() * np.sqrt(252))
            if len(excess_returns) > 1
            else 0.0
        )
        information_ratio = (
            float(excess_returns.mean() / excess_returns.std() * np.sqrt(252))
            if excess_returns.std() and excess_returns.std() > 0
            else 0.0
        )
        comparison.update(
            {
                "benchmark_total_return": float(benchmark_total_return),
                "excess_return": float(
                    performance["strategy_equity"].iloc[-1] / self.initial_capital
                    - 1
                    - benchmark_total_return
                ),
                "information_ratio": information_ratio,
                "tracking_error": tracking_error,
            }
        )
        return comparison

    def _build_metrics(self, performance: pd.DataFrame) -> dict[str, float]:
        returns = performance["strategy_returns"]
        total_return = (
            performance["strategy_equity"].iloc[-1] / self.initial_capital - 1
            if not performance.empty
            else 0.0
        )
        volatility = float(returns.std() * np.sqrt(252)) if len(returns) > 1 else 0.0
        sharpe = (
            float(returns.mean() / returns.std() * np.sqrt(252))
            if returns.std() and returns.std() > 0
            else 0.0
        )
        win_rate = float((returns > 0).sum() / len(returns)) if len(returns) else 0.0
        return {
            "strategy_total_return": float(total_return),
            "annualized_return": _annualize_from_returns(returns),
            "volatility": volatility,
            "sharpe": sharpe,
            "max_drawdown": _max_drawdown(performance["strategy_equity"]),
            "win_rate": win_rate,
            "trading_days": float(len(performance)),
        }

    def _build_trade_stats(
        self,
        trades: list[dict[str, Any]],
        round_trips: list[dict[str, float]],
    ) -> dict[str, float | int]:
        if not trades:
            return {
                "tradeCount": 0,
                "winRate": 0.0,
                "averageHoldingDays": 0.0,
                "averageTradeReturn": 0.0,
                "totalCosts": 0.0,
                "turnover": 0.0,
            }

        total_costs = sum(float(item["fee"]) + float(item["tax"]) for item in trades)
        turnover = sum(float(item["notional"]) for item in trades) / self.initial_capital
        win_rate = (
            float(sum(1 for item in round_trips if item["pnl"] > 0) / len(round_trips))
            if round_trips
            else 0.0
        )
        average_holding_days = (
            float(sum(item["holding_days"] for item in round_trips) / len(round_trips))
            if round_trips
            else 0.0
        )
        average_trade_return = (
            float(sum(item["return"] for item in round_trips) / len(round_trips))
            if round_trips
            else 0.0
        )
        return {
            "tradeCount": len(trades),
            "winRate": win_rate,
            "averageHoldingDays": average_holding_days,
            "averageTradeReturn": average_trade_return,
            "totalCosts": float(total_costs),
            "turnover": float(turnover),
        }
