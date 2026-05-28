from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

class StrategyGenerateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    description: str = Field(min_length=5, max_length=1000)

class StrategyGenerateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str = ""
    params: dict = Field(default_factory=dict)
    parameterSchema: list = Field(default_factory=list)
    explanation: str = ""
    riskNotes: list[str] = Field(default_factory=list)
    degraded: bool = False
    error: str | None = None
