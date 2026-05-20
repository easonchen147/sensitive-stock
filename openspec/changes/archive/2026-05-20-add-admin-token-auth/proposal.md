## Why

当前前后端默认入口已经切换到 Next.js + Flask，但所有页面和功能接口仍然是匿名可访问状态。这对于内部 MVP 演示和受限使用场景已经不够安全，也让后续需要接入 AI、选股、诊股等能力时缺少统一的访问控制边界。

现在推进这一轮 change 的价值在于：在不引入完整账户系统的前提下，为现有新架构补上一层最小但可用的登录鉴权能力，让“进入系统”和“调用功能”都建立在统一 token 授权之上，并把这一边界通过 OpenSpec、代码与文档一起固化下来。

## What Changes

- 新增一个基于 token 的 MVP 登录能力，提供管理员登录入口、token 签发与过期校验机制。
- 为 backend 增加统一鉴权拦截逻辑，保护现有功能 API，仅保留登录与必要运行时探针作为白名单入口。
- 为 frontend 增加登录页、登录态读取、未登录跳转、已登录访问控制与登出入口。
- 为前端 API 请求增加 token 存储与附带机制，确保页面加载和客户端交互都在登录态下访问后端。
- 明确“写死管理员账号”仅用于 MVP / 内部使用，不引入注册、用户管理、多角色、密码找回或长期正式账户体系。
- 更新 README、OpenSpec delta 与测试，确保登录边界、保护范围和非目标与代码状态一致。

## Capabilities

### New Capabilities
- `token-auth-access-control`: 定义管理员登录、token 签发与校验、受保护资源访问、MVP 账号边界和未登录拒绝策略。

### Modified Capabilities
- `flask-backend-platform`: Flask 平台要求将从“默认公开功能 API”升级为“功能 API 默认受鉴权保护，并提供统一认证错误模型”。
- `nextjs-frontend-shell`: 前端壳层要求将从“默认公开可浏览”升级为“登录后才能进入主要页面，并在请求链路中附带 token”。

## Impact

- Affected code:
  - `backend/app/__init__.py`
  - `backend/app/config.py`
  - `backend/app/errors.py`
  - `backend/app/api/*.py`
  - `backend/app/services/*`
  - `backend/tests/*`
  - `frontend/app/layout.tsx`
  - `frontend/app/page.tsx`
  - `frontend/app/backtests/page.tsx`
  - `frontend/app/market/page.tsx`
  - `frontend/app/screener/page.tsx`
  - `frontend/app/diagnosis/page.tsx`
  - `frontend/app/**/route.ts`
  - `frontend/components/*`
  - `frontend/lib/api.ts`
  - `frontend/types/api.ts`
  - `frontend/package.json`
  - `README.md`
- Affected APIs:
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/session`
  - 现有 `/api/v1/backtests/*`
  - 现有 `/api/v1/market*`
  - 现有 `/api/v1/capabilities`
  - 现有 `/api/v1/screener`
  - 现有 `/api/v1/diagnosis`
  - 现有 `/api/v1/factors`
  - 现有 `/api/v1/portfolio`
- Affected systems:
  - Flask API 鉴权边界
  - Next.js 页面路由与登录态管理
  - 前后端请求契约与错误处理
  - OpenSpec、README 与验证流程
