## Context

系统的正式能力已经跑通，但仓库中同时存在两套叙事：运行代码和前端页面已经以正式产品状态工作，主规格和少量展示文案却还保留“迁移中/骨架/占位”的老语言。由于这些老语言主要存在于主 OpenSpec、README 类文档和少量后端直接返回的展示字段，它们会持续污染后续 change、前端文案和 OpenAPI 语义。

这次改动跨越主规格、生成型契约和后端展示文案，属于小范围但跨面的收口工作。它不引入新能力，也不改变 AKQuant 回测、DeepSeek 预测或正式 API 的结构边界。

## Goals / Non-Goals

**Goals:**
- 让主 OpenSpec、运行文档和当前实现对“正式能力边界”使用同一套语言。
- 去掉当前契约中的 placeholder endpoint / migrated capability / skeleton capability 等过时语义。
- 让回测预设、回测报告说明、预测 backtest handoff 等直接渲染到前端的文案使用中文产品语言。
- 重新生成与当前描述一致的 `openapi.json` 并通过验证。

**Non-Goals:**
- 不新增或删除现有正式 API。
- 不调整 AKQuant 执行模型、DeepSeek 调用策略或前端页面信息架构。
- 不全面重写所有历史 brainstorm、archive 或 solution 文档。

## Decisions

1. 先修 OpenSpec change，再手工同步主规格与文档。  
   这次需要同时更新 requirement、主 spec Purpose、README 和迁移文档。仅依赖 archive 自动同步不足以覆盖 Purpose 和文档层，因此采用“change 记录 + 主规格手工同步 + archive 归档”的方式最稳。

2. 结构化字段保留英文标识，用户可见说明统一中文。  
   `engine=akquant`、`executionMode=next_open`、`suggestedPreset=event_theme_momentum` 这类字段是程序契约，不应被中文化；但 `description`、`summary`、`helpText`、`assumptions.detail/value`、handoff `notes` 等是直接展示文案，应改为中文产品语义。

3. OpenAPI 摘要保持契约导向，但去掉迁移期包装词。  
   OpenAPI 面向集成和前端类型层，不必强制全部中文；但 “AKQuant-backed ...” 这类描述把运行实现细节写进了契约摘要，会让 API 文档读起来像阶段性迁移结果，因此改成更中性的契约说明。

4. 本轮只改正式文档与主规格，不大规模重写历史记录。  
   历史 brainstorm、archived changes、solutions 可以保留当时的背景叙述；真正需要收口的是当前生效的 `openspec/specs/*`、README、架构/迁移文档和运行响应 copy。

## Risks / Trade-offs

- [主规格与 change delta 双轨更新] → 通过先写 change，再把主规格同步成最终状态，最后 archive `--skip-specs`，避免 archive 自动同步覆盖手工修正的 Purpose。
- [展示文案与机器字段混在同一响应对象里] → 只修改面向前端渲染的自由文本字段，避免破坏客户端依赖的键和值。
- [OpenAPI 摘要改动带来快照类测试变化] → 同步更新受影响测试，并重新生成根目录 `openapi.json` 后做全量 strict 验证。
