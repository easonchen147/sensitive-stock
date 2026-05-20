# 完成四类半成品能力 Plan

## 目标

把 `screener`、`diagnosis`、`factors`、`portfolio` 从当前 skeleton/保留模块状态升级为正式产品能力。

## 技术方案

### 后端

1. 在 `backend/app/services` 新增：
   - `screener.py`
   - `diagnosis.py`
   - `factors.py`
   - `portfolio.py`
2. 在 `backend/app/schemas` 新增对应请求/响应模型。
3. 在 `backend/app/api` 新增或替换正式蓝图逻辑。
4. 将底层 legacy 模块包裹到服务层，而不是让 API 直接触达 legacy 代码。

### 前端

1. 保留鉴权保护链路。
2. 用正式工作台替换 placeholder 页面。
3. 建立跨能力联动：
   - 筛选结果发起回测
   - 诊股页面消费 market + indicators + report
   - 因子分析与组合优化支持表格、摘要、导出

## 依赖顺序

1. 先完成 backend schemas + services。
2. 再开放 API 与测试。
3. 再接前端页面。
4. 最后接入 OpenAPI 和统一样式。

## 影响文件

- `backend/app/api/*`
- `backend/app/services/*`
- `backend/app/schemas/*`
- `backend/tests/*`
- `frontend/app/*`
- `frontend/components/*`
- `frontend/lib/*`
- `frontend/types/*`

## 测试策略

- 后端：每类能力至少有 contract test + unhappy path test。
- 前端：页面加载、失败态、关键交互与 BFF 代理测试。
- OpenSpec：spec/plan/proposal/task 全覆盖。

## 里程碑

1. `factors` / `portfolio` API 化。
2. `screener` 正式落地并支持回测联动。
3. `diagnosis` 正式落地并生成结构化报告。
4. capability inventory 从 skeleton 更新为 migrated。
