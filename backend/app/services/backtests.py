from __future__ import annotations

from .backtests_akquant import AKQuantBacktestService, serialize_symbol_result

# Compatibility export for existing imports and test seams.
LegacyBacktestService = AKQuantBacktestService

__all__ = [
    "AKQuantBacktestService",
    "LegacyBacktestService",
    "serialize_symbol_result",
]
