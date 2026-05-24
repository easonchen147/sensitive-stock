## 1. Planning and Contracts

- [x] 1.1 Finalize brainstorm, plan, proposal, design, and the `jin10-news-intelligence-pipeline` spec delta for the expanded channel network.

## 2. Source Configuration and Parsing

- [x] 2.1 Add backend config and `.env.example` entries for CLS telegraph, STCN homepage, and 21 财经资本市场频道 URLs.
- [x] 2.2 Implement a CLS page-backed news source that parses `__NEXT_DATA__` telegraph items into the shared market-news shape.
- [x] 2.3 Implement HTML headline sources for STCN and 21 财经 and normalize them into the shared market-news shape.
- [x] 2.4 Wire the new source classes into the default market news intelligence factory without changing existing API paths.

## 3. Validation

- [x] 3.1 Add source parsing tests for CLS page JSON extraction and HTML article-link extraction.
- [x] 3.2 Extend multi-source aggregation tests to cover the new channels and degraded-channel behavior.
- [x] 3.3 Run affected backend tests and `openspec validate --all --strict`.

## 4. Documentation and Assessment

- [x] 4.1 Update README and backend README with the expanded channel network and configuration.
- [x] 4.2 Reassess remaining high-value news or sentiment directions after implementation and record the next candidates.
