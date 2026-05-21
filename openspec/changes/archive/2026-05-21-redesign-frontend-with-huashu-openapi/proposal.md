## Why

当前前端已经具备可用的登录、首页、回测和行情壳层，但整体仍停留在“迁移后工作台原型 + 多个 skeleton 页面”的阶段。用户现在要求对所有页面做一次真正的产品级设计升级，并且明确指定要用 `huashu-design` 的方法完成全站视觉与交互重构，同时接入后端 `openapi.json` 覆盖的全部接口。

## What Changes

- 基于 Huashu 设计方法定义适合股票研究系统的全局页面风格、信息层级和组件语法。
- 重构登录、首页、回测、行情、选股、诊股、因子、组合等全部主页面，使它们进入统一的研究工作台语言。
- 建立基于 `openapi.json` 的前端类型/客户端接入路径，减少页面对手写漂移字段的依赖。
- 统一全站空态、错误态、degraded 态、加载态和结果解释模式。
- 用可验证的页面模板和状态规范替换当前“部分真实页面 + 部分 placeholder”的混合状态。

## Capabilities

### New Capabilities
- `frontend-research-design-system`: 定义 Huashu 驱动的研究工作台页面模板、组件语法、层级体系与状态语言。
- `openapi-driven-frontend-client`: 定义前端如何以 `openapi.json` 作为事实来源生成或对齐类型与 API client。

### Modified Capabilities
- `nextjs-frontend-shell`: 从“迁移后的应用壳层”升级为“全页面统一研究工作台 + OpenAPI 驱动的数据消费前端”。

## Impact

- Affected code:
  - `frontend/app/*`
  - `frontend/components/*`
  - `frontend/lib/*`
  - `frontend/types/*`
  - `frontend/app/globals.css`
  - 设计相关验证产物
- Affected APIs:
  - frontend 侧所有通过 BFF 或 server helper 消费的 backend OpenAPI 接口
- Affected systems:
  - application shell
  - page templates
  - frontend type/client generation
  - visual verification workflow
