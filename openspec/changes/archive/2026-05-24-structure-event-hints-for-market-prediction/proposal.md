## Why

当前系统已经拿到越来越多的公告和新闻，但 intelligence 与 prediction 仍主要围绕关键词和板块提示工作。为了让公告流真正服务于研究和回测，需要新增一层结构化事件提示，把回购、减持、股权激励、监管问询等高价值事件直接送入预测链路。

## What Changes

- 新增后端 `eventHints` 结构化事件提示能力。
- 扩展 intelligence / predictions / prediction history 契约，加入 `eventHints`。
- 升级 DeepSeek 和本地启发式预测上下文，纳入事件提示。
- 在无显式 symbols 时，自动把高优先级事件相关标的带入回测 handoff。
- 更新前端市场页以展示事件提示。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `jin10-news-intelligence-pipeline`: 扩展 intelligence 与 prediction 契约，加入结构化 `eventHints`，并要求预测上下文利用这些事件提示。

## Impact

- Affected code:
  - `backend/app/services/news_intelligence.py`
  - `backend/app/services/deepseek_prediction.py`
  - `backend/app/services/prediction_history.py`
  - `backend/app/openapi.py`
  - `backend/tests/*prediction*`
  - `frontend/types/api.ts`
  - `frontend/components/market-workbench.tsx`
  - `README.md`
  - `backend/README.md`
- APIs:
  - Existing market intelligence and prediction APIs gain an additional `eventHints` field.
- Dependencies:
  - No new third-party dependency is required.
