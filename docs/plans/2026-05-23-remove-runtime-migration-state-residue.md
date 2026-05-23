---
status: active
created: 2026-05-23
origin: user request
workflow: openspec + compound-engineering
change: remove-runtime-migration-state-residue
---

# 运行态迁移残留收口计划

## 问题框架

当前系统的主功能已经切到正式运行态：后端能力 inventory 使用 `ready / limited / disabled`，前端页面去掉了“已迁移/骨架中/规划中”的展示语义，回测也已切换到 AKQuant 主执行链路。但仓库里仍残留一层“迁移期语言”：部分主 OpenSpec 规格还在描述 `migrated / skeleton / planned / placeholder`，回测结果和预测回测交接里仍有少量英文运行时术语，`openapi.json` 与当前产品语义也没有完全收口。

这类残留不会立刻让功能不可用，但会持续制造两个问题：一是规格与运行态契约不一致，后续继续开发时容易被错误 requirement 带偏；二是前端直接渲染的后端文案仍带着迁移期或底层实现痕迹，影响产品完成度。

## 范围

本次只收口“真实运行态边界”和“用户可见后端文案”：

- 更新主 OpenSpec 规格与迁移/架构文档，使其只描述当前正式能力。
- 修正回测预设、回测结果 assumptions / insights、预测回测交接说明中的残留英文和迁移措辞。
- 调整 OpenAPI 说明文字并重新生成根目录 `openapi.json`。
- 验证后端、前端绑定、OpenSpec 和文档一致性。

本次不新增页面、不重做现有信息架构、不引入新的后端能力，也不改动 AKQuant 执行逻辑本身。

## 需求追踪

- 主 OpenSpec 不再要求 placeholder endpoint，也不再把正式能力状态描述成 `migrated / skeleton / planned`。
- 前端主规格不再把 capability inventory 解释为“迁移状态发现”，而是正式产品状态发现。
- OpenAPI 主规格和 `openapi.json` 不再出现“migrated screener”这类迁移期表述。
- 回测预设、回测 assumptions / insights、预测 backtest handoff 的用户可见文案使用简体中文产品语言。
- `prediction-history-and-evaluation` 的主规格 Purpose 不再保留 archive 生成的占位文本。
- 当前架构文档、迁移文档和 README 与真实运行边界保持一致。

## 关键决策

1. 这次按“小型 L3 收口 change”处理，而不是继续把问题散落在普通代码修补里。  
   因为问题源头在主规格，必须先修规格，再修实现和文档。

2. 不删除任何正式功能路径，只删除错误语义。  
   本轮不会撤接口或页面，只把“placeholder / migrated / skeleton”这类过时描述改成当前正式产品状态语言。

3. 后端机器字段与用户可见字段分开处理。  
   如 `engine=akquant`、`executionMode=next_open`、`suggestedPreset=event_theme_momentum` 等结构化字段保留；直接渲染给用户的说明文案改成中文产品语义。

4. 主规格采用手工同步后再 archive，archive 时跳过 spec 自动同步。  
   这次不仅要改 requirement，还要修主 spec 的 Purpose 和标题措辞；先手工同步主规格更稳，再用 archive 归档 change 记录。

## 实现单元

### U1: 计划与 OpenSpec 收口源

文件：
- `docs/plans/2026-05-23-remove-runtime-migration-state-residue.md`
- `openspec/changes/remove-runtime-migration-state-residue/proposal.md`
- `openspec/changes/remove-runtime-migration-state-residue/design.md`
- `openspec/changes/remove-runtime-migration-state-residue/tasks.md`
- `openspec/changes/remove-runtime-migration-state-residue/specs/**/spec.md`

做法：
- 先把本轮目标写成一个小型正式 change。
- 让 proposal、design、spec delta 和 tasks 都围绕“运行态真实化”和“用户可见文案收口”展开。

测试场景：
- 变更文件可通过 OpenSpec strict 校验。
- 变更范围覆盖主规格、后端可见文案、OpenAPI 与当前文档。

验证：
- `openspec validate remove-runtime-migration-state-residue --strict`

### U2: 主规格与运行文档收口

文件：
- `openspec/specs/flask-backend-platform/spec.md`
- `openspec/specs/nextjs-frontend-shell/spec.md`
- `openspec/specs/backend-openapi-publication/spec.md`
- `openspec/specs/backtest-execution-and-reporting/spec.md`
- `openspec/specs/prediction-history-and-evaluation/spec.md`
- `openspec/specs/migration-workspace-and-docs/spec.md`
- `docs/architecture/directory-map.md`
- `docs/migration/phase-one-architecture-migration.md`
- `README.md`
- `backend/README.md`

做法：
- 去掉与现状冲突的迁移期 requirement、Purpose 和文档描述。
- 统一主规格与文档对 capability inventory、正式 workbench、OpenAPI 边界和预测闭环的表述。

测试场景：
- 不再出现要求 placeholder endpoint 的主 requirement。
- 不再将正式能力状态定义为 `migrated / skeleton / planned`。
- 架构/迁移文档与当前正式页面和接口一致。

验证：
- `openspec validate --all --strict`

### U3: 后端用户文案与 OpenAPI 收口

文件：
- `backend/backtesting/presets.py`
- `backend/app/services/backtests_akquant.py`
- `backend/app/services/news_intelligence.py`
- `backend/app/openapi.py`
- `openapi.json`
- `backend/tests/test_backtests_api.py`
- `backend/tests/test_backtest_reporting_contract.py`

做法：
- 将预设说明、事件主题策略 copy、回测 assumptions / insights、预测回测交接 notes 改为中文产品语义。
- 保留机器可读字段，调整 API summary/tag description 的迁移期措辞。
- 重新生成 `openapi.json`。

测试场景：
- 预设 metadata 可直接供前端中文渲染。
- 回测结果 assumptions / insights 没有英文运行时说明残留。
- OpenAPI backtests summaries/tag descriptions 不再带 “AKQuant-backed” 迁移期包装词。

验证：
- `cd backend; uv run pytest tests/test_backtests_api.py tests/test_backtest_reporting_contract.py tests/test_market_predictions_api.py -q`
- `cd backend; uv run python scripts/generate_openapi.py --output ..\\openapi.json`

### U4: 终验、归档与知识沉淀

文件：
- `openspec/changes/archive/**`
- `docs/solutions/**`

做法：
- 跑后端测试、前端测试、OpenSpec strict 与 diff 检查。
- 使用 archive 完成本轮 change 归档。
- 补一篇 solutions 文档，说明“规格真实化 + 契约文案收口”的做法。

验证：
- `cd backend; uv run pytest -q`
- `cd backend; uv run ruff check app tests scripts`
- `cd frontend; npx tsc --noEmit --pretty false`
- `cd frontend; npm test`
- `cd frontend; npm run test:smoke`
- `openspec validate --all --strict`
- `git diff --check`

## 风险与处理

- OpenSpec delta 主要面向 requirement，同步主 spec 的 Purpose 和标题需要手工收口。  
  处理：主 spec 直接同步到最终状态，archive 时使用 `--skip-specs` 只归档记录，不再依赖自动合并。

- 回测响应里既有机器字段也有展示字段，容易误改到程序依赖的结构值。  
  处理：只调整 `description`、`summary`、`useCase`、`riskNotes`、`helpText`、`assumptions.detail/value` 等展示文案，不动 `id`、`engine`、`executionMode`、`fillPolicy` 等结构字段。

- 文档里仍有“迁移”一词时，可能是历史背景而不是错误状态。  
  处理：只收口“当前事实描述”与“正式契约”部分，归档和历史 solutions 不做全面重写。

## 验证策略

先完成 change 文档和 spec delta，再同步主规格、运行文档和后端文案，随后生成新的 `openapi.json`。验证顺序为 targeted backend tests、full backend test/ruff、frontend typecheck/test/smoke、OpenSpec strict、diff check，最后 archive 与 knowledge compounding。
