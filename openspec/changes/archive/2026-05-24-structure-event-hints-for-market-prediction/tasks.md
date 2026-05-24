## 1. Planning and Contracts

- [x] 1.1 Finalize brainstorm, plan, proposal, design, and the `jin10-news-intelligence-pipeline` spec delta for event hints.

## 2. Event Hint Pipeline

- [x] 2.1 Implement rule-based `eventHints` extraction in the news intelligence service.
- [x] 2.2 Pass `eventHints` into prediction context, prediction history, and backtest handoff symbol selection.
- [x] 2.3 Upgrade local heuristic prediction to prioritize strong event signals.

## 3. Contract and Frontend

- [x] 3.1 Extend OpenAPI and frontend types with `eventHints` and `eventHintCount`.
- [x] 3.2 Update the market workbench to render the new event hint section in Chinese.

## 4. Validation

- [x] 4.1 Add and extend backend tests for event extraction, prediction context, and API payloads.
- [x] 4.2 Regenerate `openapi.json`, run affected checks, and run `openspec validate --all --strict`.

## 5. Documentation and Assessment

- [x] 5.1 Update README and backend README with the event hint layer and automatic symbol handoff behavior.
- [x] 5.2 Reassess the next highest-value event/risk enhancements after implementation and record the next candidates.
