---
title: Structure Event Hints For Market Prediction
date: 2026-05-24
status: active
origin: docs/brainstorms/2026-05-24-structure-event-hints-for-market-prediction.md
---

# Structure Event Hints For Market Prediction Plan

## Problem Frame

系统已经接入了官方公告披露与多源新闻，但 intelligence 和 prediction 仍主要依赖关键词与板块提示，没有把高价值事件信号单独结构化。这样既浪费公告流，也让本地启发式预测缺少“事件驱动”能力。

## Scope Boundaries

本轮交付：

- 在后端新增 `eventHints` 提取与聚合。
- 让 intelligence / predictions / prediction history 保存并返回 `eventHints`。
- 升级 DeepSeek 和本地启发式预测上下文，加入 `eventHints`。
- 在没有显式 symbols 时，用事件相关标的回填 `backtestHandoff.symbols`。
- 在前端市场页展示事件提示。

本轮不交付：

- 不新增外部数据源。
- 不做公告 PDF 正文解析。
- 不引入机器学习分类器。
- 不改动回测接口结构。

## Key Decisions

- **事件结构化优先使用规则抽取。**
  当前资讯和公告已经包含标题、tags、证券代码、公告类型，足够支撑第一版规则抽取，无需引入复杂 NLP。

- **将事件层纳入 intelligence 主契约。**
  `eventHints` 与 `keywords`、`sectorHints` 并列返回，避免把事件只是塞进预测私有逻辑里。

- **本地启发式预测优先利用强事件。**
  当事件明显指向个股或强正负面时，启发式预测应优先给出事件型目标，再用板块提示补足。

- **回测交接默认复用事件相关标的。**
  用户未手工输入 symbols 时，自动交接高优先级事件涉及的股票代码，提升预测到回测的闭环效率。

- **前端只展示真实后端能力。**
  市场页只增加 `eventHints` 展示区，不新增空壳页面。

## Implementation Units

### U1: Planning and OpenSpec Artifacts

Files:

- `docs/brainstorms/2026-05-24-structure-event-hints-for-market-prediction.md`
- `docs/plans/2026-05-24-structure-event-hints-for-market-prediction.md`
- `openspec/changes/structure-event-hints-for-market-prediction/proposal.md`
- `openspec/changes/structure-event-hints-for-market-prediction/design.md`
- `openspec/changes/structure-event-hints-for-market-prediction/specs/jin10-news-intelligence-pipeline/spec.md`
- `openspec/changes/structure-event-hints-for-market-prediction/tasks.md`

Verification:

- `openspec status --change structure-event-hints-for-market-prediction --json`

### U2: Event Hint Extraction and Prediction Context

Files:

- `backend/app/services/news_intelligence.py`
- `backend/app/services/deepseek_prediction.py`
- `backend/app/services/prediction_history.py`

Approach:

- Add rule-based `eventHints` extraction over normalized items.
- Include `eventHints` in intelligence, prediction context, history storage and backtest handoff symbol selection.
- Upgrade heuristic prediction to prioritize strong event signals.

Verification:

- `poetry run pytest tests/test_event_hints_service.py tests/test_deepseek_prediction_service.py -q`

### U3: API Contract, OpenAPI, and Frontend

Files:

- `backend/app/openapi.py`
- `backend/scripts/generate_openapi.py`
- `openapi.json`
- `frontend/types/api.ts`
- `frontend/components/market-workbench.tsx`

Approach:

- Add `eventHints` schema to intelligence and predictions responses.
- Add `eventHintCount` to prediction metadata.
- Render event hints in the market workbench with Chinese labels.

Verification:

- `poetry run pytest tests/test_market_api.py tests/test_market_predictions_api.py -q`
- `cd backend && uv run python scripts/generate_openapi.py`
- `cd frontend && npm run build`

### U4: Docs and Final Validation

Files:

- `README.md`
- `backend/README.md`

Approach:

- Document the new event-hint layer and automatic symbol handoff behavior.
- Run full backend validation and OpenSpec strict validation.

Verification:

- `cd backend && poetry run pytest tests -q`
- `openspec validate --all --strict`

## Test Scenarios

- 公告和新闻项可以被规则抽取为 `eventHints`，并带出方向、评分、相关股票和来源。
- Intelligence 接口返回 `eventHints`，预测接口也返回同一结构。
- DeepSeek 上下文包含 `eventHints`，本地启发式预测在强事件出现时优先输出事件驱动预测。
- 未传 symbols 时，回测交接自动回填事件相关标的；已传 symbols 时，保留用户输入优先。
- 市场页展示事件提示，不破坏现有关键词、板块提示和预测详情区域。
