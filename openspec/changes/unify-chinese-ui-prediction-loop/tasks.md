## 1. Compound Plan And Design Source

- [x] 1.1 Write the Compound-style technical plan for Chinese UI, prediction history, evaluation, DeepSeek mode, and OpenAPI binding.
- [x] 1.2 Save the generated design reference image under `docs/design/`.
- [x] 1.3 Create the Chinese research-terminal HTML prototype under `docs/design/`.
- [x] 1.4 Create OpenSpec proposal, design, spec deltas, and task checklist.

## 2. DeepSeek V4 Flash Mode Contract

- [x] 2.1 Add backend config for DeepSeek thinking type and reasoning effort.
- [x] 2.2 Send `thinking.type` and `reasoning_effort` in DeepSeek requests and include mode fields in prediction metadata.
- [x] 2.3 Include DeepSeek mode fields in prediction cache keys and heuristic fallback metadata.
- [x] 2.4 Extend DeepSeek prediction tests for enabled, disabled, cache, and fallback modes.

## 3. Source Quality, History, Detail, And Evaluation Backend

- [x] 3.1 Add source-quality scoring and quality notes to multi-source news payloads.
- [x] 3.2 Add local JSONL prediction history service with bounded list, detail lookup, and corrupt-line tolerance.
- [x] 3.3 Store prediction runs with stable `runId` and per-row `predictionId`.
- [x] 3.4 Add protected history, detail, and evaluation endpoints under market news routes.
- [x] 3.5 Add backend tests for history persistence, detail lookup, evaluation, and source-quality scoring.

## 4. OpenAPI And Frontend Contract

- [x] 4.1 Publish new prediction-loop paths and schemas in backend OpenAPI.
- [x] 4.2 Regenerate root `openapi.json`.
- [x] 4.3 Update frontend OpenAPI route bindings and API types.
- [x] 4.4 Update frontend API helpers for prediction history, detail, evaluation, and thinking-mode query overrides.
- [x] 4.5 Verify OpenAPI publication and frontend binding tests.

## 5. Chinese UI And Unified Research Terminal

- [ ] 5.1 Replace application shell, login, dashboard, and auth copy with Chinese-only UI language.
- [ ] 5.2 Replace market page copy and layout with the unified Chinese research-terminal style.
- [ ] 5.3 Add market prediction detail, source-quality, history, DeepSeek mode, and evaluation panels.
- [ ] 5.4 Replace backtest page labels, table headers, buttons, status text, and result metadata with Chinese UI language.
- [ ] 5.5 Replace screener, diagnosis, factor, and portfolio page labels, buttons, empty states, and result text with Chinese UI language.
- [ ] 5.6 Update global CSS tokens and responsive layout to match the saved design direction.
- [ ] 5.7 Update smoke tests to assert Chinese page titles and representative workbench entry.

## 6. Verification, Archive, And Compound Learning

- [ ] 6.1 Run targeted backend tests for prediction, news, history, market API, and OpenAPI.
- [ ] 6.2 Run backend full tests and ruff.
- [ ] 6.3 Run frontend tests, build, and browser smoke tests.
- [ ] 6.4 Run Playwright screenshot checks for desktop and mobile layouts.
- [ ] 6.5 Run `openspec validate --all --strict` and `git diff --check`.
- [ ] 6.6 Run OpenSpec verify for this change and fix any findings.
- [ ] 6.7 Archive the completed OpenSpec change.
- [ ] 6.8 Write a Compound solution document for the Chinese research terminal and prediction-loop pattern.
