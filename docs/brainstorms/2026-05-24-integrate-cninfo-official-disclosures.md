# Integrate CNInfo Official Disclosures Brainstorm

Created: 2026-05-24
Status: active

## 背景

当前市场资讯链路已经具备：

- `Jin10NewsService` 作为主快讯源，带官方接口和公开 fallback。
- `MultiSourceNewsService` 作为聚合器，已经接入东方财富、新浪、财联社、证券时报和 21 财经。
- `MarketNewsIntelligenceService` 负责关键词、板块提示、DeepSeek 预测和回测 handoff。

上一轮已经补强了媒体与快讯覆盖，但高价值的“官方公告披露”仍未进入聚合主链路。相比泛媒体快讯，公告披露具备更高的事件密度、更稳定的结构化字段和更强的研究价值。

## 当前调研结论

本轮优先接入 `CNInfo` 官方公告披露接口：

- 页面：`https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice`
- 实际数据接口：`POST https://www.cninfo.com.cn/new/disclosure`
- 关键参数：
  - `column`
  - `pageNum`
  - `pageSize`
  - `clusterFlag`
- 可用列值已经在前端脚本中暴露，包括：
  - `szse_latest`
  - `sse_latest`
  - `bj_latest`

实测结论：

- `clusterFlag=false` 时，接口直接返回平铺 `announcements` 列表，最适合本轮聚合。
- 数据字段包含：
  - `announcementId`
  - `announcementTitle`
  - `announcementTime`
  - `announcementTypeName`
  - `secCode`
  - `secName`
  - `adjunctUrl`
  - `important`
- `adjunctUrl` 可拼接到 `https://static.cninfo.com.cn/` 形成可访问 PDF 链接。

## 本轮范围

- 新增第一批官方披露渠道：
  - 巨潮公告-深市
  - 巨潮公告-沪市
  - 巨潮公告-北交所
- 将这些渠道接入 `MultiSourceNewsService`，保持现有 `/api/v1/market/news*` 契约不变。
- 为新增源补充配置项、解析测试、聚合测试和文档说明。
- 在返回项中尽量保留公告类型、证券简称和证券代码，以增强后续关键词和主题抽取。

## 非目标

- 本轮不直接对接上交所、深交所官网各自的监管问询或处分页。
- 不抓取公告 PDF 正文，不做全文解析和摘要抽取。
- 不新增公告专属 API 路径或前端独立页面。
- 不引入需要登录态或签名算法的披露接口。

## 成功标准

- `/api/v1/market/news`、`/api/v1/market/news/intelligence`、`/api/v1/market/news/predictions` 可以返回官方公告披露内容。
- `channels` 中能看到新增的巨潮公告渠道状态。
- 单个公告源失败不会拖垮整体聚合；所有上游失败时仍遵守缓存降级语义。
- 公告项包含稳定的标题、发布时间、PDF 链接、证券简称/代码和公告类型标签。
- 后端测试、OpenSpec 校验和文档更新通过。

## 后续候选

- 接入上交所监管问询、纪律处分与审核动态页面。
- 接入深交所监管函、关注函、问询函页面。
- 为官方公告增加“事件类型分桶”，把股东大会、回购、减持、股权激励、业绩预告等直接转成预测上下文。
