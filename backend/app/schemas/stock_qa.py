from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator

class StockQARequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    question: str = Field(min_length=2, max_length=2000)
    symbols: list[str] = Field(default_factory=list)

    @field_validator("symbols", mode="before")
    @classmethod
    def normalize_symbols(cls, value):
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [s.strip() for s in value.split(",") if s.strip()]
        return [str(s).strip() for s in (value or []) if str(s).strip()]
