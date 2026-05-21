## 1. Shared Backend Foundation

- [x] 1.1 为 `screener`、`diagnosis`、`factors`、`portfolio` 设计统一 schema、错误模型与 metadata 约定。
- [x] 1.2 在 `backend/app/services` 中建立四类能力的正式 service 边界，并补充依赖注入点。

## 2. Factors And Portfolio API-ization

- [x] 2.1 为因子分析补正式请求/响应 schema、service 包装与 API 路由。
- [x] 2.2 为组合优化补正式请求/响应 schema、service 包装与 API 路由。
- [x] 2.3 为 `factors` / `portfolio` 增加后端 contract tests、失败态测试与 capability inventory 状态更新。

## 3. Screener Workbench

- [x] 3.1 实现结构化筛选模板、自然语言到筛选条件的转换层与结果序列化。
- [x] 3.2 为 `screener` 增加导出能力、结果排序/过滤与回测回灌接口或跳转契约。
- [x] 3.3 为 `screener` 增加后端测试、前端工作台页面与关键交互测试。

## 4. Diagnosis Reporting

- [x] 4.1 实现诊股所需的行情、技术指标、上下文聚合与结构化报告 service。
- [x] 4.2 为 `diagnosis` 增加正式 API、失败兜底与降级 metadata。
- [x] 4.3 为 `diagnosis` 增加前端工作台页面、报告渲染与错误态验证。

## 5. Integration And Documentation

- [x] 5.1 更新 capability inventory、前端首页与导航状态，使四类能力脱离 skeleton 状态。
- [x] 5.2 将四类能力纳入 OpenAPI 契约、README 与相关文档说明。
- [x] 5.3 运行 OpenSpec 校验与前后端定向测试，验证四类能力与回测/行情链路衔接。
