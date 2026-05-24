## 1. Dependencies and Configuration

- [x] 1.1 Upgrade AkShare to `1.18.63` and add TickFlow `0.1.21` in `backend/pyproject.toml`.
- [x] 1.2 Add TickFlow environment configuration to backend config and `.env.example`.
- [x] 1.3 Refresh `backend/poetry.lock` and `backend/uv.lock`.

## 2. Market Data Providers

- [x] 2.1 Add a lazy TickFlow historical provider with A-share symbol conversion and shared OHLCV normalization.
- [x] 2.2 Update `SmartDataProvider` to include TickFlow, configurable provider order, last-success metadata, and provider error diagnostics.
- [x] 2.3 Add optional TickFlow quote fallback after AkShare and before EastMoney direct.
- [x] 2.4 Add backend tests for provider order, TickFlow normalization, selected-source metadata, and quote fallback.

## 3. AKQuant Backtest Enhancements

- [x] 3.1 Extend backtest request schemas for volume limit, fee floor, transfer fee, and strategy-level risk fields.
- [x] 3.2 Pass supported advanced controls to AKQuant with stable `signal_replay` strategy identity.
- [x] 3.3 Collect AKQuant runtime event summaries and enrich metrics when additional AKQuant values are available.
- [x] 3.4 Return `dataQuality`, `executionQuality`, `riskDiagnostics`, and `engineEvents` for each symbol result.
- [x] 3.5 Add backend API and reporting tests for the expanded request and response contract.

## 4. OpenAPI and Frontend

- [x] 4.1 Update backend OpenAPI component schemas for expanded backtest request and diagnostic response fields.
- [x] 4.2 Regenerate root `openapi.json`.
- [x] 4.3 Update frontend API types and backtest payload builder.
- [x] 4.4 Update the回测页面 with Chinese advanced controls and diagnostic result panels.
- [x] 4.5 Update frontend tests for the expanded payload and summary output.

## 5. Documentation and Verification

- [x] 5.1 Update README and backend README with AkShare/TickFlow configuration, source order, and advanced backtest controls.
- [x] 5.2 Run focused backend tests, frontend tests/build, OpenAPI generation checks, and `openspec validate --all --strict`.
- [x] 5.3 Verify the OpenSpec change against implementation, archive the change, and add a Compound solution note.
