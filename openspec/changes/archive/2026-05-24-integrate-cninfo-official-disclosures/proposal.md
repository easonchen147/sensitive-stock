## Why

当前市场资讯链路已经覆盖多个媒体快讯与新闻站点，但仍缺少官方公告披露源。对于 A 股研究和预测，上交所、深交所、北交所公司的法定公告比普通媒体快讯更稳定、更结构化，也更适合提炼事件驱动线索。

## What Changes

- 新增 `CNInfo` 官方公告披露源。
- 第一批默认接入深市、沪市、北交所三个公告流。
- 为新增源补充配置项、测试和文档说明。
- 保持现有 `/api/v1/market/news*` 路径与响应结构不变。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `jin10-news-intelligence-pipeline`: 扩展默认多源资讯聚合要求，加入 CNInfo 官方公告披露源，并明确公告类型、证券简称和 PDF 链接会被标准化进共享 market-news 结构。

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
  - Existing market news APIs return richer official披露 coverage, but no path changes.
- Dependencies:
  - No new third-party Python dependency is required.
