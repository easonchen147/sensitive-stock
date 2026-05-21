from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DEFAULT_RESEARCH_UNIVERSE = ["000001", "600000", "300750", "000858", "601318"]


class DateRangeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")

    @model_validator(mode="after")
    def validate_dates(self) -> "DateRangeRequest":
        if self.end_date < self.start_date:
            raise ValueError("endDate must be on or after startDate")
        return self


class ScreenerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    min_price: float | None = Field(default=None, alias="minPrice", ge=0)
    max_price: float | None = Field(default=None, alias="maxPrice", ge=0)
    min_change_percent: float | None = Field(default=None, alias="minChangePercent")
    max_change_percent: float | None = Field(default=None, alias="maxChangePercent")
    sectors: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_ranges(self) -> "ScreenerFilters":
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.max_price < self.min_price
        ):
            raise ValueError("maxPrice must be greater than or equal to minPrice")
        if (
            self.min_change_percent is not None
            and self.max_change_percent is not None
            and self.max_change_percent < self.min_change_percent
        ):
            raise ValueError("maxChangePercent must be greater than or equal to minChangePercent")
        return self


class ScreenerRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    universe: list[str] = Field(default_factory=lambda: list(DEFAULT_RESEARCH_UNIVERSE))
    prompt: str | None = None
    filters: ScreenerFilters = Field(default_factory=ScreenerFilters)
    sort_by: Literal["score", "price", "changePercent"] = Field(default="score", alias="sortBy")
    limit: int = Field(default=10, ge=1, le=50)
    backtest_start_date: date | None = Field(default=None, alias="backtestStartDate")
    backtest_end_date: date | None = Field(default=None, alias="backtestEndDate")

    @field_validator("universe", mode="before")
    @classmethod
    def normalize_universe(cls, value: object) -> list[str]:
        if value is None or value == "":
            return list(DEFAULT_RESEARCH_UNIVERSE)
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = value
        normalized = [str(item).strip() for item in items if str(item).strip()]
        if not normalized:
            raise ValueError("universe must contain at least one symbol")
        return normalized


class ScreenerExportRequest(ScreenerRunRequest):
    format: Literal["json", "csv"] = "json"


class DiagnosisRequest(DateRangeRequest):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    symbol: str = Field(min_length=6, max_length=12)
    include_news: bool = Field(default=True, alias="includeNews")


class FactorAnalysisRequest(DateRangeRequest):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    symbol: str = Field(min_length=6, max_length=12)
    factors: list[str] = Field(default_factory=list)
    forward_days: int = Field(default=5, alias="forwardDays", ge=1, le=60)
    top_n: int = Field(default=5, alias="topN", ge=1, le=20)


class PortfolioOptimizationRequest(DateRangeRequest):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    symbols: list[str] = Field(min_length=2, max_length=20)
    objective: Literal["equal_weight", "minimum_variance", "maximum_sharpe", "risk_parity"] = (
        "maximum_sharpe"
    )
    risk_free_rate: float = Field(default=0.03, alias="riskFreeRate", ge=0, le=1)

    @field_validator("symbols", mode="before")
    @classmethod
    def normalize_symbols(cls, value: object) -> list[str]:
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = value or []
        normalized = [str(item).strip() for item in items if str(item).strip()]
        if len(normalized) < 2:
            raise ValueError("symbols must contain at least two stock codes")
        return normalized
