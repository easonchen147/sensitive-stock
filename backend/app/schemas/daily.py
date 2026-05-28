from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DailyRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    universe: list[str] = Field(default_factory=list)

    @field_validator("universe", mode="before")
    @classmethod
    def normalize_universe(cls, value):
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [s.strip() for s in value.split(",") if s.strip()]
        return [str(s).strip() for s in (value or []) if str(s).strip()]


class DailyHistoryQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    limit: int = Field(default=20, ge=1, le=100)
