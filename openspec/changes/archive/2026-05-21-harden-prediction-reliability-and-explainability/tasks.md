## 1. Planning And OpenSpec Source

- [x] 1.1 Write the Compound plan document for prediction reliability and explainability.
- [x] 1.2 Create OpenSpec proposal, design, spec deltas, and tasks for `harden-prediction-reliability-and-explainability`.

## 2. DeepSeek Prediction Reliability

- [x] 2.1 Add prompt/schema versioning, explicit JSON schema prompt example, and enriched input metadata.
- [x] 2.2 Add successful-remote prediction TTL caching keyed by normalized context, model, and schema version.
- [x] 2.3 Add tests for JSON contract, cache hit, cache-key symbol sensitivity, and fallback metadata.

## 3. Source Quality And Dedupe Explainability

- [x] 3.1 Add `sourceQuality` and `dedupeMetadata` to multi-source news aggregation payloads.
- [x] 3.2 Preserve that metadata through intelligence and prediction responses.
- [x] 3.3 Add tests for duplicate counts, failed channel counts, and prediction metadata preservation.

## 4. OpenAPI And Frontend Contract

- [x] 4.1 Update OpenAPI schemas and generated `openapi.json` for the enriched metadata.
- [x] 4.2 Update frontend API types and contract tests for the new fields.

## 5. Market Workbench Display

- [x] 5.1 Render cache/model/schema state, source-quality counts, dedupe counts, and source evidence.
- [x] 5.2 Verify frontend unit tests, build, and smoke flow.

## 6. Verification, Archive, And Compound Learning

- [x] 6.1 Run backend pytest, ruff, frontend tests/build/smoke, OpenSpec strict validation, and diff checks.
- [x] 6.2 Archive the OpenSpec change after verification passes.
- [x] 6.3 Write a Compound solution note for prediction reliability and explainability.
