## 1. Planning and Contracts

- [x] 1.1 Finalize brainstorm, plan, proposal, design, and the `jin10-news-intelligence-pipeline` spec delta for CNInfo official disclosures.

## 2. Source Configuration and Parsing

- [x] 2.1 Add backend config and `.env.example` entries for CNInfo disclosure endpoint and static PDF base URL.
- [x] 2.2 Implement a reusable CNInfo disclosure source that fetches flat announcement rows for a configured market column and normalizes them into the shared market-news shape.
- [x] 2.3 Wire SZSE, SSE, and BSE CNInfo disclosure sources into the default market news intelligence factory without changing existing API paths.

## 3. Validation

- [x] 3.1 Add parser tests for CNInfo official disclosure list normalization.
- [x] 3.2 Extend multi-source aggregation tests to cover the new official disclosure channels and degraded-channel behavior.
- [x] 3.3 Run affected backend tests and `openspec validate --all --strict`.

## 4. Documentation and Assessment

- [x] 4.1 Update README and backend README with the official disclosure layer and configuration.
- [x] 4.2 Reassess the next highest-value official exchange/supervision directions after implementation and record the next candidates.
