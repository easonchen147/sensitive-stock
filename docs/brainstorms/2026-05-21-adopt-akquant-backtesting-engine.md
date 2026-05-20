# AKQuant 回测替换 Brainstorm

## 背景

当前仓库里的回测已经比最早版本强，但本质仍是自维护 legacy stack：

- 自定义 `backtesting/*` 引擎、pipeline、策略预设与数据适配。
- 已经做过一次 AKQuant-inspired 的升级，但仍不是第三方标准引擎。

用户这次的要求更明确：

> 如果涉及回测功能，希望升级为 `akfamily/akquant`，直接用第三方库全面取代现有回测实现。

因此这次不是继续“借鉴 AKQuant 思路”，而是要评估并规划真实替换。

## 官方事实基线

基于本轮联网核实，AKQuant 有官方 GitHub 仓库与文档站点，应以该项目的真实 API、执行模型与依赖边界为准，而不是延续旧 proposal 里“只迁思想”的路径。

## 需要回答的问题

### 1. 替换边界到底多大？

可能有三种级别：

1. **内核替换**：只替换 backend backtest engine，保留现有 Flask API 形状。
2. **契约替换**：后端与前端都改成贴近 AKQuant 的参数、运行与结果模型。
3. **产品替换**：以 AKQuant 为中心重建策略目录、执行设置、报表展示与导出路径。

用户要求“全面取代现有回测”，因此提案必须覆盖至少 2 和 3 的路线，而不是停在 1。

### 2. 与现有自定义策略能力如何兼容？

当前系统保留了 AI 生成策略 / 自定义代码路径。AKQuant 若采用不同的策略接口，就要决定：

- 是否保留旧 `generate_signals(data, ctx)` 作为适配层；
- 是否引入策略模板编译 / 适配器；
- 是否分离“内置策略”和“用户自定义策略”。

### 3. 对前端意味着什么？

如果彻底替换引擎，前端不应再继续假设旧返回字段。需要同步升级：

- 输入表单
- 预设目录
- 执行参数
- 指标与图表
- 回测报告导出

## 推荐方向

### 主张

把 AKQuant 作为新的唯一回测内核，现有 `backend/backtesting/*` 转入兼容层 / 迁移层，逐步收敛直至删除。

### 理由

- 避免长期维护一套半自研引擎。
- 为后续选股回灌、组合研究、因子验证提供统一引擎底座。
- 让 OpenAPI、前端工作台、策略目录都围绕真实第三方能力建模。

## 高风险点

- 第三方依赖稳定性与版本锁定。
- 现有测试、前端字段、策略执行接口可能大面积变更。
- 若 AKQuant 的多资产/事件驱动模型与当前系统假设不一致，需明确适配层。

## 成功标准

- 现有 `POST /api/v1/backtests/run` 和相关预设目录改由 AKQuant 驱动。
- 旧 `backend/backtesting/*` 不再承担主执行职责。
- OpenSpec、README、OpenAPI、前端类型全部以 AKQuant 集成为准。

## 与其他提案关系

- 是 `complete-skeleton-capabilities` 中“选股回灌回测闭环”的关键前置。
- 是 `complete-backend-openapi-platform` 中回测 API 章节的重要组成部分。
- 是 `redesign-frontend-with-huashu-openapi` 中回测页面改版的基础输入。
