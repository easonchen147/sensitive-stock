## 1. 契约与测试基线

- [x] 1.1 为回测 preset metadata 与 richer backtest report 字段补充 backend 定向测试。
- [x] 1.2 为前端回测 helper 的表单校验、快速配置和结果摘要逻辑补充 Vitest 测试。

## 2. Backend 回测增强

- [x] 2.1 扩展 `backtesting/presets.py` 与相关序列化逻辑，向前端暴露更完整的策略说明与参数帮助 metadata。
- [x] 2.2 在回测执行/序列化链路中补充更强的解释型结果字段，使前端可直接渲染假设摘要与关键 insight。
- [x] 2.3 更新 Flask backtest schema / service / API 输出，保持现有路由稳定并对齐新的类型契约。

## 3. 前端 UI / UX 升级

- [x] 3.1 重构共享应用壳层、全局样式 token 与 capability brief 组件，统一页面视觉层级、状态语义与占位表达。
- [x] 3.2 升级首页 capability inventory 与总览布局，使其准确表达真实迁移完成度和当前可用入口。
- [x] 3.3 重做回测工作台交互，落地分组输入、快速配置、参数解释、加载/空/错状态和解释型结果展示。
- [x] 3.4 将市场页升级为真实消费 backend market/news API 的工作台，并实现 watchlist、板块切换和 degraded/error 状态。

## 4. 文档、Review 与验证

- [x] 4.1 更新 README 与迁移文档，确保页面完成度、市场页状态和回测增强边界与代码一致。
- [x] 4.2 进行实现自查，修正设计不一致、冗余和无关改动。
- [x] 4.3 运行 OpenSpec 校验、backend 测试、frontend 测试/类型检查/构建与必要 smoke，确认前后端契约对齐。
