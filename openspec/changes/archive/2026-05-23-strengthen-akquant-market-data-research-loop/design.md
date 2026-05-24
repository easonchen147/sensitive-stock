## Context

Sensitive Stock is now a frontend/backend separated A-share research system. The backend already uses AkShare for market data and AKQuant for backtests, while the frontend consumes backend APIs through the global OpenAPI contract. The current limitation is not the absence of a backtest path, but that the system still hides important execution assumptions and has limited market-data resilience when AkShare is unstable.

The user asked to prioritize `tickflow-org/tickflow`, upgrade AkShare, continue mining AKQuant, and reference `daily_stock_analysis`. The relevant design lesson from `daily_stock_analysis` is explicit provider priority, fallbacks, error diagnostics, and richer research context. This change applies those ideas within the current backend/frontend architecture without adding unsupported frontend pages.

## Goals / Non-Goals

**Goals:**

- Keep AkShare as default A-share primary source and upgrade it to the latest confirmed backend pin.
- Add TickFlow as an optional historical market-data provider and optional quote fallback.
- Surface data-source diagnostics in market overview and backtest reports.
- Expose AKQuant-supported volume, fee, and strategy-level risk controls through the structured backtest contract.
- Keep existing backtest response fields compatible while adding richer diagnostic sections.
- Update OpenAPI and frontend types/UI so the new contract is actually callable.

**Non-Goals:**

- Do not implement search-engine providers or social-sentiment APIs in this change.
- Do not add frontend navigation for capabilities that lack backend implementation.
- Do not replace AkShare with TickFlow as the default source.
- Do not introduce root-level Python runtime files or revive Streamlit-era structure.

## Decisions

### Decision: Keep AkShare Primary, Add TickFlow as Explicit Optional Source

Default historical source order becomes `akshare -> tickflow -> tushare -> sina_direct`. If `BACKEND_MARKET_DATA_PREFER_TICKFLOW=true`, order becomes `tickflow -> akshare -> tushare -> sina_direct`.

Rationale:

- AkShare is already the system's primary normalized A-share source.
- TickFlow free tier is valuable for historical day K data, but realtime quote support requires an API key.
- A source-order switch lets users intentionally compare TickFlow behavior without silently changing default data semantics.

Alternative considered:

- Make TickFlow the default primary source. Rejected because it would change research output by default and could surprise existing users.

### Decision: Lazy Import and Lazy Client Creation

TickFlow is imported and instantiated inside provider methods, not at module import time.

Rationale:

- Backend startup must not fail if optional provider setup is unavailable or an API key is absent.
- Tests can inject fake clients without network access.
- TickFlow free client prints a notice; lazy creation reduces noisy startup behavior.

Alternative considered:

- Instantiate all providers eagerly. Rejected because it makes optional integrations harder to degrade cleanly.

### Decision: Use `signal_replay` as AKQuant Strategy ID

AKQuant strategy-level risk maps use a stable strategy ID `signal_replay`.

Rationale:

- The adapter currently executes one replay strategy per symbol, so the strategy identity is the adapter strategy, not the symbol.
- AKQuant strategy-level fields are keyed by strategy ID.
- Using a stable ID makes event summaries and diagnostics consistent.

Alternative considered:

- Key strategy risk maps by symbol. Rejected because it conflates strategy identity with instrument identity.

### Decision: Add Diagnostic Objects Instead of Replacing Existing Metrics

Each symbol result adds:

- `dataQuality`
- `executionQuality`
- `riskDiagnostics`
- `engineEvents`

Existing `metrics`, `comparison`, `series`, `tradeStats`, `trades`, `assumptions`, and `insights` remain.

Rationale:

- This is backwards-compatible for existing frontend code and API consumers.
- It separates performance metrics from data-source and execution realism diagnostics.

Alternative considered:

- Fold diagnostics into `metrics`. Rejected because source quality and engine events are not performance metrics.

## Risks / Trade-offs

- TickFlow API shape or permission limits may vary by tier -> provider handles missing dependency, empty responses, permission errors, and network errors as degraded provider failures.
- Lockfile refresh may alter transitive packages -> run focused backend tests and `poetry check` after lock refresh.
- AKQuant strategy risk controls may reject invalid values -> schema bounds keep fields non-negative and only pass maps when values are explicitly enabled.
- More frontend controls can make the回测页面 heavier -> group advanced controls under existing execution/cost/risk sections and keep labels in Chinese.
- External data-source differences can change回测 results -> response reports selected source and fallback diagnostics so result provenance is visible.

## Migration Plan

1. Add specs and tasks for the change.
2. Update dependencies and configuration.
3. Implement TickFlow provider and market-data diagnostics.
4. Extend backtest schema and AKQuant runtime adapter.
5. Sync OpenAPI and frontend contract/UI.
6. Update documentation and run validation.
7. Archive the OpenSpec change after verification passes.

Rollback strategy:

- Set `BACKEND_MARKET_DATA_ENABLE_TICKFLOW=false` to remove TickFlow from provider order without changing code.
- Set `BACKEND_MARKET_DATA_PREFER_TICKFLOW=false` to return to AkShare-first behavior.
- Existing backtest clients can omit all new fields and continue using current defaults.

## Open Questions

- None blocking for this change. Full search-provider and social-sentiment integrations should be handled as separate OpenSpec changes because they require API-key strategy, quota handling, and product placement decisions.
