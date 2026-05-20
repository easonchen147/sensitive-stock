from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BacktestMarketRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbols: list[str] = Field(min_length=1, max_length=5)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    adjust: Literal["", "qfq", "hfq"] = "qfq"
    benchmark_symbol: str | None = Field(default=None, alias="benchmarkSymbol")

    @field_validator("symbols", mode="before")
    @classmethod
    def normalize_symbols(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = value or []

        normalized = [str(item).strip() for item in items if str(item).strip()]
        if not normalized:
            raise ValueError("symbols must contain at least one stock code")
        return normalized


class BacktestStrategyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    mode: Literal["preset", "custom"] = "custom"
    preset_id: str | None = Field(default=None, alias="presetId")
    code: str = ""
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_mode(self) -> "BacktestStrategyRequest":
        if self.mode == "preset" and not self.preset_id:
            raise ValueError("preset 模式下必须提供 presetId")
        if self.mode == "custom" and not self.code:
            raise ValueError("custom 模式下必须提供 strategyCode")
        return self


class BacktestExecutionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    mode: Literal["close", "next_open"] = "close"
    position_size: float = Field(default=1.0, alias="positionSize", gt=0, le=1)
    lot_size: int = Field(default=100, alias="lotSize", ge=1)


class BacktestCostRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    trading_fee: float = Field(default=0.0005, alias="tradingFee", ge=0)
    stamp_tax: float = Field(default=0.001, alias="stampTax", ge=0)
    slippage: float = Field(default=0.0, ge=0)


class BacktestRiskRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    stop_loss: float = Field(default=0.0, alias="stopLoss", ge=0)
    take_profit: float = Field(default=0.0, alias="takeProfit", ge=0)


class BacktestRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    market: BacktestMarketRequest
    strategy: BacktestStrategyRequest
    execution: BacktestExecutionRequest = Field(default_factory=BacktestExecutionRequest)
    costs: BacktestCostRequest = Field(default_factory=BacktestCostRequest)
    risk: BacktestRiskRequest = Field(default_factory=BacktestRiskRequest)
    initial_capital: float = Field(default=100000.0, alias="initialCapital", gt=0)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_payload(cls, payload: Any) -> Any:
        if not isinstance(payload, dict):
            return payload
        if "market" in payload or "strategy" in payload:
            return payload

        return {
            "market": {
                "symbols": payload.get("symbols"),
                "startDate": payload.get("startDate"),
                "endDate": payload.get("endDate"),
                "adjust": payload.get("adjust", "qfq"),
                "benchmarkSymbol": payload.get("benchmarkSymbol"),
            },
            "strategy": {
                "mode": payload.get("strategyMode", "custom"),
                "presetId": payload.get("strategyPreset"),
                "code": payload.get("strategyCode", ""),
                "params": payload.get("params", {}),
            },
            "execution": {
                "mode": payload.get("executionMode", "close"),
                "positionSize": payload.get("positionSize", 1.0),
                "lotSize": payload.get("lotSize", 100),
            },
            "costs": {
                "tradingFee": payload.get("tradingFee", 0.0005),
                "stampTax": payload.get("stampTax", 0.001),
                "slippage": payload.get("slippage", 0.0),
            },
            "risk": {
                "stopLoss": payload.get("stopLoss", 0.0),
                "takeProfit": payload.get("takeProfit", 0.0),
            },
            "initialCapital": payload.get("initialCapital", 100000.0),
        }

    @model_validator(mode="after")
    def validate_dates(self) -> "BacktestRunRequest":
        if self.market.end_date < self.market.start_date:
            raise ValueError("endDate must be on or after startDate")
        return self

    @property
    def symbols(self) -> list[str]:
        return self.market.symbols

    @property
    def start_date(self) -> date:
        return self.market.start_date

    @property
    def end_date(self) -> date:
        return self.market.end_date

    @property
    def adjust(self) -> str:
        return self.market.adjust

    @property
    def benchmark_symbol(self) -> str | None:
        return self.market.benchmark_symbol

    @property
    def strategy_code(self) -> str:
        return self.strategy.code

    @property
    def strategy_mode(self) -> str:
        return self.strategy.mode

    @property
    def strategy_preset(self) -> str | None:
        return self.strategy.preset_id

    @property
    def params(self) -> dict[str, Any]:
        return self.strategy.params

    @property
    def execution_mode(self) -> str:
        return self.execution.mode

    @property
    def position_size(self) -> float:
        return self.execution.position_size

    @property
    def lot_size(self) -> int:
        return self.execution.lot_size

    @property
    def trading_fee(self) -> float:
        return self.costs.trading_fee

    @property
    def stamp_tax(self) -> float:
        return self.costs.stamp_tax

    @property
    def slippage(self) -> float:
        return self.costs.slippage

    @property
    def stop_loss(self) -> float:
        return self.risk.stop_loss

    @property
    def take_profit(self) -> float:
        return self.risk.take_profit
