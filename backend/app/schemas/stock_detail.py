from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StockDetailQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbol: str = Field(min_length=6, max_length=12)


class KlineQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbol: str = Field(min_length=6, max_length=12)
    period: Literal[
        "daily", "weekly", "monthly", "60min", "30min", "15min", "5min"
    ] = "daily"
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")


class FinancialSummaryQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbol: str = Field(min_length=6, max_length=12)


class StockNewsQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbol: str = Field(min_length=6, max_length=12)
    limit: int = Field(default=10, ge=1, le=50)
