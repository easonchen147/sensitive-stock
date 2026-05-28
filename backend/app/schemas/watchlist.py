from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1, max_length=10)
    name: str | None = None
    cost_price: float | None = Field(default=None, ge=0)
    shares: float | None = Field(default=None, ge=0)
    note: str | None = Field(default=None, max_length=200)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v.strip())
        if len(digits) != 6:
            raise ValueError("symbol must contain exactly 6 digits")
        return digits


class WatchlistUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    cost_price: float | None = Field(default=None, ge=0)
    shares: float | None = Field(default=None, ge=0)
    note: str | None = Field(default=None, max_length=200)


class WatchlistItemResponse(BaseModel):
    symbol: str
    name: str
    cost_price: float
    shares: float
    note: str
    added_at: str
    updated_at: str


class WatchlistResponse(BaseModel):
    items: list[WatchlistItemResponse]
