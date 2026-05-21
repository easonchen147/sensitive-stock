"""
Compatibility helpers retained during the AKQuant migration.

The primary execution path now lives in backend/app/services/backtests_akquant.py.
Modules here remain available for market-data access, preset metadata, and the
legacy generate_signals(data, ctx) strategy DSL used by the AKQuant adapter.
"""
