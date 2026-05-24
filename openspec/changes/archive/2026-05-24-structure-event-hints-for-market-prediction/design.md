## Context

现有资讯架构已经稳定：

- `MultiSourceNewsService` 负责多源聚合与去重。
- `MarketNewsIntelligenceService` 负责关键词、板块提示、预测和回测 handoff。
- `DeepSeekMarketPredictionService` 负责远程模型和本地启发式预测。

本轮只在这条链路中补上一层“事件提示”，不重构整体架构。

## Goals / Non-Goals

**Goals:**

- 抽取可解释的结构化 `eventHints`。
- 让事件提示进入 intelligence、prediction、history 和前端展示。
- 让启发式预测和回测交接对强事件更敏感。

**Non-Goals:**

- 不做 PDF 正文解析。
- 不引入机器学习事件分类器。
- 不新增市场页之外的新页面。

## Decisions

### Decision: 用规则映射做第一版事件结构化

基于标题、内容和 tags 中已有的公告类型、证券简称、证券代码与关键词，映射出第一版事件类型。

Rationale:

- 当前字段已足够支持高价值事件抽取。
- 可解释、可测试、可快速调整。

Alternative considered:

- 使用大模型即时分类。Rejected，因为会引入新的不确定性和成本。

### Decision: `eventHints` 与 `keywords`、`sectorHints` 并列

事件提示是 intelligence 层的一等公民，不应只在预测内部隐式使用。

Rationale:

- 前端和历史记录都需要看到它。
- 便于后续扩展风险面板和事件工作流。

### Decision: 启发式预测优先使用强事件

当事件明确指向个股或正负面方向时，启发式预测优先输出事件型结果，再用板块提示补足。

Rationale:

- 回购、减持、监管问询等事件比普通关键词更有研究价值。
- 有助于把预测和回测连接得更自然。

### Decision: 事件相关标的可自动进入回测交接

若用户未手工传 symbols，则使用高优先级 `eventHints` 中提取的股票代码回填 `backtestHandoff.symbols`。

Rationale:

- 提升“资讯 -> 预测 -> 回测”的闭环效率。
- 保留用户手工输入优先，不干扰明确操作。

## Risks / Trade-offs

- 规则分类会有边界误差 -> 用测试和显式事件词表控制。
- 事件太多会让前端拥挤 -> 前端只显示高优先级前几项。
- 自动回填 symbols 可能带出噪声标的 -> 仅使用高评分事件，并保留用户输入优先。

## Migration Plan

1. 新增 `eventHints` 提取逻辑。
2. 将其接入 intelligence、prediction、history 与 OpenAPI。
3. 更新前端类型和市场页展示。
4. 跑测试、生成 OpenAPI、更新文档。

Rollback:

- 删除 `eventHints` 生成与展示逻辑即可回到关键词 / 板块提示版本。

## Open Questions

- 本轮无阻塞问题。后续若要做可配置权重表或监管风险专题面板，应单独开新 change。
