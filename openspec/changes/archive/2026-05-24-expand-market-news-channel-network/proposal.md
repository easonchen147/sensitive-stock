## Why

当前资讯聚合链路已经支持 Jin10、东方财富、新浪和 DeepSeek 预测，但可用渠道仍偏少。继续增强新闻源能提升题材覆盖度和预测上下文质量，同时必须避免接入当前不可用、失真或空白的公开 feed。

## What Changes

- 新增财联社电报页解析源，直接利用页面内嵌的 `__NEXT_DATA__` 电报列表。
- 新增证券时报首页标题聚合源。
- 新增 21世纪经济报道证券频道标题聚合源。
- 为新增渠道补充配置项、测试和文档说明。
- 保持现有 `/api/v1/market/news*` 契约不变，继续复用 `channels`、`sourceQuality`、`dedupeMetadata` 和降级语义。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `jin10-news-intelligence-pipeline`: 扩展多源资讯聚合要求，加入 CLS、证券时报和 21 财经的页面解析渠道，并明确对质量差的公开 feed 不应作为默认正式源接入。

## Impact

- Affected code:
  - `backend/app/services/news_intelligence.py`
  - `backend/app/api/market.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/*news*`
  - `README.md`
  - `backend/README.md`
- APIs:
  - Existing market news APIs return more source coverage, but no path changes.
- Dependencies:
  - No new third-party Python dependency is required.
