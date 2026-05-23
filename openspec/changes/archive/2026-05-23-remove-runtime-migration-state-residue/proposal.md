## Why

当前系统已经进入正式运行态，但主 OpenSpec、部分运行文档和少量后端可见文案仍残留迁移期表述，导致规格、实现和用户看到的内容并不完全一致。现在需要把这些“迁移残影”收口掉，避免后续继续沿着过时契约开发。

## What Changes

- 修正主 OpenSpec 对 capability inventory、formal workbench、OpenAPI 覆盖面和预测闭环的运行态描述，不再要求 placeholder endpoint 或 `migrated / skeleton / planned` 状态。
- 收口回测预设、回测 assumptions / insights 和预测回测交接说明中的用户可见英文及底层运行时措辞。
- 更新 README、后端 README、架构文档、迁移文档与当前正式能力边界对齐。
- 调整 OpenAPI backtests 相关 summary/tag description，并重新生成根目录 `openapi.json`。

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `flask-backend-platform`: capability inventory 与 formal capability surface 改为正式运行态语言，不再描述 placeholder endpoint。
- `nextjs-frontend-shell`: capability inventory 与正式页面语义改为运行态产品状态，而不是迁移状态发现。
- `backend-openapi-publication`: OpenAPI 覆盖面描述改为正式 API 契约语言，不再保留 migrated phrasing。
- `backtest-execution-and-reporting`: 回测预设与结果解释文案 requirement 明确要求直接可渲染的产品语言。
- `prediction-history-and-evaluation`: 预测持久化和回测交接 requirement 收口为正式研究语义。
- `migration-workspace-and-docs`: 运行文档 requirement 改为描述当前正式页面和接口，不再保留 skeleton 页面事实。

## Impact

- Affected code: `backend/backtesting/presets.py`, `backend/app/services/backtests_akquant.py`, `backend/app/services/news_intelligence.py`, `backend/app/openapi.py`
- Affected generated artifact: `openapi.json`
- Affected docs/specs: `openspec/specs/*`, `README.md`, `backend/README.md`, `docs/architecture/directory-map.md`, `docs/migration/phase-one-architecture-migration.md`
- Affected verification: backtest API/reporting tests, prediction API tests, OpenSpec strict validation, frontend smoke/type checks
