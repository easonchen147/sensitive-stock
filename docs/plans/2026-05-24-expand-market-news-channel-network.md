---
title: Expand Market News Channel Network
date: 2026-05-24
status: active
origin: docs/brainstorms/2026-05-24-expand-market-news-channel-network.md
---

# Expand Market News Channel Network Plan

## Problem Frame

当前资讯聚合链路已经能支撑多源新闻、DeepSeek 预测和回测交接，但有效渠道仍偏少，且现有聚合对“公开页面可解析数据”的利用不足。用户希望继续增强资讯来源数量和覆盖度，但不能为追求数量引入当前失真、空白或握手不稳定的渠道。

## Scope Boundaries

本轮交付：

- 新增 `财联社电报页`、`证券时报首页`、`21世纪经济报道证券频道` 三个资讯源。
- 将新渠道纳入现有 `MultiSourceNewsService` 聚合、去重、质量评分和降级逻辑。
- 新增对应配置项、测试和文档说明。

本轮不交付：

- 不新增 API 路径或前端页面。
- 不做详情页全文抓取。
- 不引入需要登录、签名或付费额度的资讯 API。
- 不把 RSS 异常或空白渠道硬接入生产链路。

## Key Decisions

- **优先接入真实可解析页面，而不是质量不稳定的公开 RSS。**
  `CLS` 页面直接嵌入 JSON，`STCN` 和 `21财经` 页面具有稳定标题链接结构，当前可用性明显高于 `Sina RSS / Ifeng RSS`。

- **新增 source 继续复用现有响应契约。**
  保持 `items/channels/sourceQuality/dedupeMetadata` 结构不变，避免新增前端契约成本。

- **对 HTML 标题类渠道采用标题级聚合。**
  `STCN` 和 `21财经` 只抓标题、链接和可见时间线索，不额外抓详情页，控制复杂度和请求成本。

- **对页面嵌入 JSON 的渠道做结构化解析优先。**
  `CLS` 优先读取 `__NEXT_DATA__` 中的 `telegraphList`，而不是从 DOM 文本反向剥离。

- **失败策略保持“单渠道失败不拖垮整体”。**
  新渠道必须遵守 MultiSource 聚合的失败告警、降级和缓存回退模式。

## Implementation Units

### U1: Planning and OpenSpec Artifacts

Files:

- `docs/brainstorms/2026-05-24-expand-market-news-channel-network.md`
- `docs/plans/2026-05-24-expand-market-news-channel-network.md`
- `openspec/changes/expand-market-news-channel-network/proposal.md`
- `openspec/changes/expand-market-news-channel-network/design.md`
- `openspec/changes/expand-market-news-channel-network/tasks.md`
- `openspec/changes/expand-market-news-channel-network/specs/jin10-news-intelligence-pipeline/spec.md`

Verification:

- `openspec status --change expand-market-news-channel-network --json`

### U2: Source Configuration

Files:

- `backend/app/config.py`
- `backend/.env.example`
- `backend/app/api/market.py`

Approach:

- Add default URLs for `CLS` telegraph page, `STCN` homepage, and `21财经` capital channel page.
- Wire the new source classes into the default `NEWS_INTELLIGENCE_SERVICE_FACTORY`.

Verification:

- `poetry run pytest tests/test_market_predictions_api.py -q`

### U3: News Source Parsing and Aggregation

Files:

- `backend/app/services/news_intelligence.py`

Approach:

- Add a `ClsTelegraphNewsSource` that parses page-embedded `__NEXT_DATA__` JSON.
- Add lightweight HTML headline sources for `STCN` and `21财经`.
- Normalize output into the shared market-news shape and reuse existing dedupe + quality scoring.

Verification:

- `poetry run pytest tests/test_multisource_news_service.py tests/test_extended_market_news_sources.py -q`

### U4: Tests, Docs, and Validation

Files:

- `backend/tests/test_extended_market_news_sources.py`
- `backend/tests/test_multisource_news_service.py`
- `README.md`
- `backend/README.md`

Approach:

- Add parsing tests for page JSON and HTML article-link extraction.
- Extend aggregation tests to include the new channels and failure semantics.
- Update docs to describe the expanded channel network and the reason RSS-like channels were not chosen for the first batch.

Verification:

- `cd backend && poetry run pytest tests -q`
- `openspec validate --all --strict`

## Test Scenarios

- `ClsTelegraphNewsSource` extracts title, content, author, time, and detail URL from a sample `__NEXT_DATA__` payload.
- `StcnArticleListSource` only keeps valid article-detail links and ignores empty or decorative anchors.
- `TwentyOneJingjiArticleListSource` keeps capital-channel article links and normalizes relative URLs.
- `MultiSourceNewsService` merges new source results with Jin10 / Eastmoney / Sina and still reports accurate `channels` and `sourceQuality`.
- If one of the new page sources fails, the aggregated response remains available and marks the failure in `warnings`.
- If all sources fail after a previous success, cached degraded payload behavior remains unchanged.
