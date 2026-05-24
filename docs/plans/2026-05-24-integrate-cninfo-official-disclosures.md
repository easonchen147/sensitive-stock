---
title: Integrate CNInfo Official Disclosures
date: 2026-05-24
status: active
origin: docs/brainstorms/2026-05-24-integrate-cninfo-official-disclosures.md
---

# Integrate CNInfo Official Disclosures Plan

## Problem Frame

当前多源资讯链路对媒体快讯已经有一定覆盖，但仍缺少官方公告披露数据。对于 A 股研究和事件驱动预测，公告披露通常比媒体快讯更直接、更结构化，也更容易沉淀成稳定的事件线索。

## Scope Boundaries

本轮交付：

- 新增 `CNInfo` 官方公告披露源。
- 第一批接入深市、沪市、北交所三个 `column`。
- 将公告源接入现有 `MultiSourceNewsService` 聚合、去重、质量评分和降级逻辑。
- 新增对应配置、测试和文档说明。

本轮不交付：

- 不新增公告专属接口或前端页面。
- 不解析公告 PDF 正文。
- 不接入上交所/深交所监管问询、处分或审核页。
- 不改变现有市场新闻响应契约。

## Key Decisions

- **优先使用 CNInfo 的结构化官方公告接口。**
  相比 HTML 硬刮，`/new/disclosure` 已提供稳定字段和可配置市场列，更适合生产接入。

- **按市场拆成多个 source，而不是混成一个总源。**
  深市、沪市、北交所分别作为独立 channel，便于质量观测、失败隔离和后续优先级调整。

- **保留公告元字段到 tags 与内容占位中。**
  将 `announcementTypeName`、`secName`、`secCode` 写入 tags，并用“证券简称 + 公告标题 + 公告类型”构造内容占位，增强下游关键词抽取。

- **继续复用现有 market-news 契约。**
  不新增接口路径，仍输出 `items/channels/sourceQuality/dedupeMetadata/warnings`。

- **官方公告仍遵守单渠道失败不拖垮整体的聚合语义。**
  新 source 只影响 coverage，不改变主链路的容错模型。

## Implementation Units

### U1: Planning and OpenSpec Artifacts

Files:

- `docs/brainstorms/2026-05-24-integrate-cninfo-official-disclosures.md`
- `docs/plans/2026-05-24-integrate-cninfo-official-disclosures.md`
- `openspec/changes/integrate-cninfo-official-disclosures/proposal.md`
- `openspec/changes/integrate-cninfo-official-disclosures/design.md`
- `openspec/changes/integrate-cninfo-official-disclosures/tasks.md`
- `openspec/changes/integrate-cninfo-official-disclosures/specs/jin10-news-intelligence-pipeline/spec.md`

Verification:

- `openspec status --change integrate-cninfo-official-disclosures --json`

### U2: CNInfo Source Configuration

Files:

- `backend/app/config.py`
- `backend/.env.example`
- `backend/app/api/market.py`

Approach:

- Add configurable CNInfo disclosure endpoint and static PDF base URL.
- Wire three market-specific CNInfo source instances into the default `NEWS_INTELLIGENCE_SERVICE_FACTORY`.

Verification:

- `poetry run pytest tests/test_market_predictions_api.py -q`

### U3: Official Disclosure Parsing and Aggregation

Files:

- `backend/app/services/news_intelligence.py`

Approach:

- Add a generic `CninfoDisclosureNewsSource` that calls `/new/disclosure` with a configurable `column`.
- Normalize CNInfo rows into the shared market-news shape.
- Reuse existing dedupe, quality scoring and channel failure semantics.

Verification:

- `poetry run pytest tests/test_multisource_news_service.py tests/test_cninfo_disclosure_news_source.py -q`

### U4: Tests, Docs, and Validation

Files:

- `backend/tests/test_cninfo_disclosure_news_source.py`
- `backend/tests/test_multisource_news_service.py`
- `README.md`
- `backend/README.md`

Approach:

- Add parser tests for CNInfo list payloads and normalization.
- Extend aggregation tests to include the new official disclosure channels.
- Update docs to explain the official disclosure layer and configuration.

Verification:

- `cd backend && poetry run pytest tests -q`
- `openspec validate --all --strict`

## Test Scenarios

- `CninfoDisclosureNewsSource` requests the configured `column` with `clusterFlag=false` and parses flat `announcements`.
- CNInfo rows normalize to title, published time, tags, importance, PDF URL and source identifiers.
- Multiple CNInfo market sources can coexist with Jin10 / Eastmoney / Sina / CLS / STCN / 21 财经 and still produce stable `channels` and `sourceQuality`.
- If one official disclosure source fails, the aggregated payload remains available and records the failed channel in `warnings`.
- If CNInfo returns no usable rows for a market, that source reports a channel failure instead of silently producing broken items.
