from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .data import HistoricalDataRequest, SmartDataProvider
from .engine import Backtester, BacktestResult
from .presets import resolve_strategy_source
from .strategy import StrategyExecutor


@dataclass
class BacktestRequest:
    symbol: str
    start_date: str
    end_date: str
    strategy_code: str = ""
    initial_capital: float = 100000.0
    trading_fee: float = 0.0005
    stamp_tax: float = 0.001
    slippage: float = 0.0
    adjust: str = "qfq"
    stop_loss: float = 0.0
    take_profit: float = 0.0
    params: dict[str, Any] = field(default_factory=dict)
    execution_mode: str = "close"
    position_size: float = 1.0
    lot_size: int = 100
    benchmark_symbol: str | None = None
    strategy_mode: str = "custom"
    strategy_preset: str | None = None


class BacktestService:
    def __init__(self) -> None:
        self._executor = StrategyExecutor()

    def run(self, request: BacktestRequest) -> BacktestResult:
        provider = SmartDataProvider()
        warnings: list[str] = []
        resolved_code, preset = resolve_strategy_source(
            mode=request.strategy_mode,
            preset_id=request.strategy_preset,
            custom_code=request.strategy_code,
        )

        data = provider.get_ohlcv(
            HistoricalDataRequest(
                symbol=request.symbol,
                start_date=request.start_date,
                end_date=request.end_date,
                adjust=request.adjust,
            )
        )

        benchmark = None
        if request.benchmark_symbol:
            try:
                benchmark = provider.get_ohlcv(
                    HistoricalDataRequest(
                        symbol=request.benchmark_symbol,
                        start_date=request.start_date,
                        end_date=request.end_date,
                        adjust=request.adjust,
                    )
                )
            except Exception as exc:
                warnings.append(f"基准 {request.benchmark_symbol} 获取失败，已跳过对比: {exc}")

        signal = self._executor.execute(resolved_code, data, request.params)
        backtester = Backtester(
            initial_capital=request.initial_capital,
            trading_fee=request.trading_fee,
            stamp_tax=request.stamp_tax,
            slippage=request.slippage,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            execution_mode=request.execution_mode,
            position_size=request.position_size,
            lot_size=request.lot_size,
        )
        settings = {
            "symbol": request.symbol,
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
            **provider.describe_sources(),
        }
        return backtester.run(
            data,
            signal,
            benchmark=benchmark,
            settings=settings,
            warnings=warnings,
        )
