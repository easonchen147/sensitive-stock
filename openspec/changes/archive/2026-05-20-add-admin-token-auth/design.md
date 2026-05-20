## Context

当前仓库的默认运行形态已经是 `frontend/` + `backend/` 双运行时：Next.js 提供页面与交互，Flask 提供版本化 API。问题在于，这套新壳层虽然已经能访问回测、市场、能力清单和一系列 placeholder 路由，但默认完全公开，没有统一的登录入口、没有登录态存储策略、也没有对 API 的统一鉴权拦截。

这一轮登录能力不是在旧 Streamlit 中补一个表单，而是要在迁移后的前后端结构上建立一条完整链路：

- backend 需要提供管理员登录、token 签发、token 校验和功能接口保护；
- frontend 需要提供登录页、未登录重定向、登录态读取和带 token 的请求链路；
- 文档与 OpenSpec 需要明确说明：这是单管理员、内部 MVP、无注册、无多角色、无账户中心的最小实现。

这个 change 同时涉及安全边界、跨模块路由、前后端请求方式和测试策略，属于典型的跨切面设计改动。

## Goals / Non-Goals

**Goals:**

- 为当前 Next.js + Flask 架构增加一套可实际运行的登录鉴权能力。
- 使用 token-based authorization 思路，为 backend 功能 API 建立统一的 Bearer Token 校验边界。
- 仅提供一个内置管理员账号，满足内部 MVP / 受限使用场景。
- 让所有主要页面和现有功能接口都在登录后才能访问。
- 让 frontend 同时覆盖页面保护、登录流程、token 存储和请求附带。
- 通过测试、OpenSpec、README 和 archive 保证边界表达一致。

**Non-Goals:**

- 本轮不实现注册、密码找回、邮箱验证、短信验证码、修改密码或用户自助资料管理。
- 本轮不实现多角色权限、细粒度 RBAC、组织租户、审计后台或会话吊销列表。
- 本轮不引入数据库用户表或完整 IAM / OAuth provider；“OAuth token / token-based authorization 思路”仅体现在 Bearer Token 授权模型，而不是完整第三方 OAuth 登录。
- 本轮不把 legacy `app.py` / `pages/*.py` 重新拉回主链路作为登录承载面。

## Decisions

### 1. Backend 使用“单管理员账号 + 签名限时 Bearer Token”，而不是引入完整账户系统或 JWT 依赖

backend 将新增一个专用 auth service：

- 固定一个内置管理员账号，用于 MVP / 内部使用；
- 登录成功后签发带时间戳的签名 token；
- 后续受保护 API 统一通过 `Authorization: Bearer <token>` 校验；
- token 解析后得到最小身份信息，例如 `sub=admin`、`role=admin`、`scope=internal_mvp`。

技术上优先使用 Flask 已带依赖的 `itsdangerous` 来签发和校验限时 token，而不是额外引入 JWT 包。原因是：

- 当前只有单管理员账号和单应用 consumer，不需要 JWT 生态里的复杂 claim 和公私钥管理；
- `itsdangerous` 已随 Flask 依赖链存在，实现成本低、可读性高；
- 可以做到签名、防篡改、过期校验，满足这轮 MVP 边界。

管理员账号边界：

- 默认提供一套写死管理员凭据，保证仓库拉起后即可登录；
- 同时允许通过环境变量覆盖用户名、密码和 token secret，避免把“写死账号”误解为长期正式方案；
- 设计与文档都必须明确：这是内部 MVP 兜底账户，不代表未来账户体系。

备选方案：

- 引入 JWT（如 `PyJWT`）。
  - 放弃原因：对当前单管理员 MVP 来说过重，增加依赖和密钥管理复杂度。
- 直接使用 Flask session / server-side session。
  - 放弃原因：用户明确要求采用 token-based authorization 思路，且 backend / frontend 是双运行时，Bearer Token 更适合作为统一接口边界。

### 2. Backend 在应用级 `before_request` 做统一鉴权拦截，只保留最小白名单

backend 会在应用工厂里注册统一鉴权钩子，而不是在每个蓝图里手写重复校验。规则如下：

- 默认保护所有 `/api/v1/*` 功能接口；
- 仅对白名单路径放行：
  - `POST /api/v1/auth/login`
  - `GET /api/v1/health`
  - `OPTIONS` 预检请求
- 缺失 token、格式错误、签名错误、过期 token 统一返回结构化 `401` 错误；
- 通过校验后将当前身份写入请求上下文，供后续需要用户信息的处理器复用。

这样可以把“功能接口默认受保护”做成平台级约束，而不是依赖开发者记得给某个新路由补 decorator。

备选方案：

- 为每个蓝图或每个 handler 单独加装饰器。
  - 放弃原因：容易漏掉 route，不符合“所有功能接口都需要登录后访问”的硬边界要求。

### 3. Frontend 使用“httpOnly Cookie 存储 token + BFF 风格 route handler 转发”，而不是把 token 暴露给浏览器脚本

frontend 需要同时解决两件事：

- 页面访问控制
- 客户端组件调用 backend 时如何附带 token

设计选择是：

- 登录页提交到 Next.js 自身的 `/api/auth/login` route handler；
- route handler 代 backend 登录接口发起请求，成功后把返回 token 写入 frontend 域下的 `httpOnly` cookie；
- frontend 客户端组件不直接读取 token，而是调用 Next.js 内部 `/api/backend/...` 代理 route；
- 这些代理 route 从 `httpOnly` cookie 中读取 token，并转发到 Flask backend，同时自动补 `Authorization` 头。

这样带来的收益是：

- token 不暴露给 `window.localStorage`、`sessionStorage` 或普通 JS 可读 cookie；
- 客户端组件无需知道 backend token 细节，只消费同域 API；
- server component / route handler 都能在服务端读取 cookie，并统一携带鉴权头。

备选方案：

- 直接把 token 存在 `localStorage`，客户端请求时自行附带。
  - 放弃原因：XSS 暴露面更大，且不利于 server-side 页面保护。
- 让 backend 直接下发跨端口 cookie。
  - 放弃原因：本地双端口开发下 cookie 域与跨站策略更麻烦，不如由 Next.js 自己持有前端登录态。

### 4. Frontend 同时使用 middleware 和 server-side session 校验，保证“未登录不能进页面”

页面保护需要覆盖“没有 cookie”与“cookie 存在但 token 无效/过期”两种情况，因此使用双层保护：

- `middleware.ts`：快速检查登录 cookie 是否存在；没有则把用户从受保护页面重定向到 `/login`；
- 页面级 server helper：在受保护页面渲染前，通过 frontend 自身的 session 校验逻辑确认 token 仍有效；若后端返回 `401`，则清掉 cookie 并重定向到 `/login`。

这样可以兼顾性能和正确性：

- 大部分未登录访问在 middleware 阶段就被挡住；
- 过期或伪造 cookie 不会因为“仅检查存在性”而绕过真正的页面保护。

登录页本身会反向处理：

- 已登录用户访问 `/login` 时直接回到首页；
- 登录成功后默认跳转到首页或原始目标页。

备选方案：

- 只做客户端 `useEffect` 跳转。
  - 放弃原因：会出现先渲染再跳转的闪烁，不满足“未登录不能访问功能页面”的要求。

### 5. 页面和接口保护范围以“主链路默认全部保护，运维探针最小豁免”为准

受保护范围：

- Frontend 页面：
  - `/`
  - `/backtests`
  - `/market`
  - `/screener`
  - `/diagnosis`
- Backend 功能接口：
  - `/api/v1/capabilities`
  - `/api/v1/backtests/*`
  - `/api/v1/market*`
  - `/api/v1/screener`
  - `/api/v1/diagnosis`
  - `/api/v1/factors`
  - `/api/v1/portfolio`
  - `/api/v1/auth/session`

白名单范围：

- `/login` 页面
- `POST /api/v1/auth/login`
- `GET /api/v1/health`
- frontend 自身静态资源与 Next.js 内部资源

说明：

- `health` 保持公开，用于本地开发和最小运维探针；
- `auth/login` 必须公开，否则无法建立会话；
- 不额外引入注册入口，因此也不存在注册白名单。

### 6. 测试策略优先验证“默认拒绝、成功登录、已登录可用、前端代理自动带 token”

这轮验证会围绕以下风险点构建：

- backend 未携带 token 时必须返回 `401`
- backend 登录成功后必须能访问原本受保护的路由
- frontend 登录 route 必须正确写 cookie
- frontend backend proxy 必须从 cookie 读取 token 并向 Flask 附带 `Authorization`
- frontend 页面 guard 至少要覆盖“未登录跳登录页”和“已登录可进入主页面”的关键逻辑

由于当前 frontend 还没有浏览器级 E2E 框架，本轮 smoke 采用：

- backend Flask test client
- frontend Vitest + TypeScript + `next build`
- 必要的开发服务脚本级 smoke（登录前后访问受保护 route / API）

## Risks / Trade-offs

- `[写死管理员账号存在天然泄露风险]` → 通过明确 internal MVP 边界、允许环境变量覆盖、限制为单账号且不在最终总结里重复明文凭据来降低风险。
- `[token 无服务端吊销能力]` → 通过较短 TTL、登出清 cookie、MVP 边界说明来控制；本轮不实现黑名单与 refresh token。
- `[frontend 增加 BFF 代理层会多一跳]` → 只对需要登录态的前端请求使用，换取 httpOnly cookie 与统一鉴权转发能力。
- `[middleware 只检查 cookie 存在性]` → 再叠加页面级 session 校验，避免失效 token 误放行。
- `[现有测试需要整体补 auth 头]` → 通过测试 helper 统一生成登录 token，避免在每个测试里手写重复逻辑。

## Migration Plan

1. 先补 OpenSpec artifacts，明确 auth 范围、边界和非目标。
2. 先写 backend 鉴权失败/成功测试，再实现 auth service、登录 API 和 request guard。
3. 再补 frontend 登录与代理测试，实现登录页、cookie session、请求代理和页面保护。
4. 更新 README，使运行方式、默认管理员边界和验证命令与新行为一致。
5. 完成 code review、自测和 OpenSpec 校验后再 archive。

回滚策略：

- 若前端保护链路出现问题，可暂时关闭 frontend route handler 对 backend 的代理调用并回退到未合并状态；本轮不会修改已有业务 API 路径，因此功能回滚边界清晰。
- backend 的 auth 改动集中在新增 auth service、auth blueprint 和统一拦截逻辑，必要时可通过移除拦截注册快速回到公开访问模型。

## Open Questions

- 当前没有阻塞性开放问题。
- 默认假设仅需单个内置管理员账号；如果后续需要第二个内部账号或可配置账号列表，应作为下一轮 change 单独设计，而不是在本轮内扩成简易用户系统。
