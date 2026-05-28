from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MarketQuotesQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbols: list[str] = Field(min_length=1)

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


class MarketSectorsQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    limit: int = Field(default=5, ge=1, le=50)
    sector_type: Literal["concept", "industry"] = Field(
        default="concept",
        alias="sectorType",
    )


class MarketNewsQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    limit: int = Field(default=100, ge=1, le=100)
    symbols: list[str] = Field(default_factory=list)
    thinking: Literal["enabled", "disabled"] | None = None
    reasoning_effort: Literal["high", "max"] | None = Field(
        default=None,
        alias="reasoningEffort",
    )

    @field_validator("symbols", mode="before")
    @classmethod
    def normalize_symbols(cls, value: Any) -> list[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = value or []
        return [str(item).strip() for item in items if str(item).strip()]


class MarketCompareQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    symbols: list[str] = Field(min_length=2, max_length=5)

    @field_validator("symbols", mode="before")
    @classmethod
    def normalize_symbols(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            items = value.split(",")
        else:
            items = value or []

        normalized = [str(item).strip() for item in items if str(item).strip()]
        if len(normalized) < 2:
            raise ValueError("symbols must contain at least 2 stock codes")
        if len(normalized) > 5:
            raise ValueError("symbols must contain at most 5 stock codes")
        return normalized


class PredictionHistoryQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    limit: int = Field(default=20, ge=1, le=100)
