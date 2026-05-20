from __future__ import annotations

from typing import Any

import pandas as pd


class LegacyBacktestService:
    def list_presets(self) -> dict[str, list[dict[str, Any]]]:
        from backtesting.presets import serialize_strategy_presets

        return serialize_strategy_presets()

    def run_batch(self, request) -> dict[str, list[dict[str, Any]]]:  # noqa: ANN001
        from backtesting.pipeline import BacktestRequest, BacktestService

        runner = BacktestService()
        results: list[dict[str, Any]] = []
        failures: list[dict[str, str]] = []

        for symbol in request.symbols:
            try:
                legacy_request = BacktestRequest(
                    symbol=symbol,
                    start_date=request.start_date.isoformat(),
                    end_date=request.end_date.isoformat(),
                    strategy_code=request.strategy_code,
                    initial_capital=request.initial_capital,
                    trading_fee=request.trading_fee,
                    stamp_tax=request.stamp_tax,
                    slippage=request.slippage,
                    adjust=request.adjust,
                    stop_loss=request.stop_loss,
                    take_profit=request.take_profit,
                    params=request.params,
                    execution_mode=request.execution_mode,
                    position_size=request.position_size,
                    lot_size=request.lot_size,
                    benchmark_symbol=request.benchmark_symbol,
                    strategy_mode=request.strategy_mode,
                    strategy_preset=request.strategy_preset,
                )
                result = runner.run(legacy_request)
                results.append(serialize_symbol_result(symbol, result))
            except Exception as exc:
                failures.append({"symbol": symbol, "message": str(exc)})

        return {"results": results, "failures": failures}


def serialize_symbol_result(symbol: str, result) -> dict[str, Any]:  # noqa: ANN001
    settings = dict(result.settings)
    metrics = dict(result.metrics)
    comparison = dict(result.comparison)
    warnings = list(result.warnings)
    trade_stats = _build_trade_stats_payload(
        trade_stats=result.trade_stats,
        performance=result.performance,
        settings=settings,
    )

    return {
        "symbol": symbol,
        "settings": settings,
        "metrics": metrics,
        "comparison": comparison,
        "series": _serialize_series(result),
        "tradeStats": trade_stats,
        "trades": _serialize_trades(result.trades),
        "warnings": warnings,
        "assumptions": _build_assumptions(settings),
        "insights": _build_insights(
            metrics=metrics,
            comparison=comparison,
            trade_stats=trade_stats,
            warnings=warnings,
        ),
    }


def _serialize_series(result) -> dict[str, list[dict[str, Any]]]:  # noqa: ANN001
    performance: pd.DataFrame = result.performance
    return {
        "equity": _series_rows(performance, "strategy_equity"),
        "benchmark": _series_rows(performance, "bench_equity"),
        "drawdown": _series_rows(performance, "drawdown"),
        "position": _series_rows(performance, "position"),
        "cash": _series_rows(performance, "cash"),
        "monthlyReturns": _monthly_rows(result.monthly_returns),
    }


def _series_rows(performance: pd.DataFrame, column: str) -> list[dict[str, Any]]:
    if column not in performance.columns:
        return []

    rows: list[dict[str, Any]] = []
    for index, value in performance[column].items():
        if pd.isna(value):
            continue
        rows.append(
            {
                "date": pd.Timestamp(index).strftime("%Y-%m-%d"),
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


def _serialize_trades(trades: pd.DataFrame) -> list[dict[str, Any]]:
    if trades.empty:
        return []

    records: list[dict[str, Any]] = []
    for _, row in trades.iterrows():
        records.append(
            {
                "date": pd.Timestamp(row["date"]).strftime("%Y-%m-%d"),
                "action": str(row["action"]),
                "reason": str(row.get("reason") or ""),
                "price": float(row["price"]),
                "shares": int(row["shares"]),
                "notional": float(row["notional"]),
                "fee": float(row["fee"]),
                "tax": float(row["tax"]),
            }
        )
    return records


def _build_trade_stats_payload(
    *,
    trade_stats: dict[str, Any],
    performance: pd.DataFrame,
    settings: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(trade_stats)
    if performance.empty:
        payload.setdefault("endingEquity", float(settings.get("initialCapital") or 0.0))
        payload.setdefault("netProfit", 0.0)
        payload.setdefault("exposureRate", 0.0)
        return payload

    initial_capital = float(
        settings.get("initialCapital") or performance["strategy_equity"].iloc[0]
    )
    ending_equity = float(performance["strategy_equity"].iloc[-1])
    exposure_rate = (
        float((performance["position"] > 0).sum() / len(performance))
        if "position" in performance.columns and len(performance)
        else 0.0
    )

    payload["endingEquity"] = ending_equity
    payload["netProfit"] = float(ending_equity - initial_capital)
    payload["exposureRate"] = exposure_rate
    return payload


def _build_assumptions(settings: dict[str, Any]) -> list[dict[str, str]]:
    execution_mode = str(settings.get("executionMode") or "close")
    execution_detail = (
        "信号变化后的下一交易日开盘成交；最后一根 K 线若缺少下一日开盘价会忽略该次变动。"
        if execution_mode == "next_open"
        else "信号变化当日按收盘价成交。"
    )
    stop_loss = float(settings.get("stopLoss") or 0.0)
    take_profit = float(settings.get("takeProfit") or 0.0)
    risk_value = (
        f"止损 {stop_loss * 100:.1f}% / 止盈 {take_profit * 100:.1f}%"
        if stop_loss > 0 or take_profit > 0
        else "止损 关闭 / 止盈 关闭"
    )

    return [
        {
            "label": "执行模式",
            "value": execution_mode,
            "detail": execution_detail,
        },
        {
            "label": "仓位与手数",
            "value": (
                f"仓位 {float(settings.get('positionSize') or 0.0) * 100:.0f}% / "
                f"手数 {int(settings.get('lotSize') or 0)}"
            ),
            "detail": "按 A 股整手成交，超出现金可承受范围时会自动缩减成交股数。",
        },
        {
            "label": "交易成本",
            "value": (
                f"佣金 {float(settings.get('tradingFee') or 0.0) * 100:.2f}% / "
                f"印花税 {float(settings.get('stampTax') or 0.0) * 100:.2f}% / "
                f"滑点 {float(settings.get('slippage') or 0.0) * 100:.2f}%"
            ),
            "detail": "买入计佣金，卖出同时计佣金和印花税，成交价按滑点调整。",
        },
        {
            "label": "风险控制",
            "value": risk_value,
            "detail": "止损止盈按日内 high / low 触发强制平仓。",
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
    insights.append(
        {
            "title": "回撤画像",
            "tone": "positive" if abs(max_drawdown) <= 0.1 else "warning",
            "detail": (
                f"最大回撤 {abs(max_drawdown) * 100:.2f}%，"
                f"年化收益 {float(metrics.get('annualized_return') or 0.0) * 100:.2f}%。"
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
