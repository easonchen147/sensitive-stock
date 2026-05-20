## 1. 鉴权契约与测试基线

- [x] 1.1 为 backend 增加登录、session、未授权访问和受保护接口的定向测试。
- [x] 1.2 为 frontend 增加登录态辅助逻辑、token 代理转发或会话处理的定向测试。

## 2. Backend 登录与接口保护

- [x] 2.1 增加 auth 配置、管理员账号校验、签名 token 签发与解析服务。
- [x] 2.2 增加 `POST /api/v1/auth/login`、`GET /api/v1/auth/session` 并统一认证错误模型。
- [x] 2.3 在 Flask 应用层增加鉴权拦截，保护现有功能 API 并保留最小白名单。

## 3. Frontend 登录与页面保护

- [x] 3.1 增加登录页、登录提交流程、登出入口和受保护页面的 session guard。
- [x] 3.2 增加前端 auth route handler 与 backend 代理转发，使 token 以受控方式存储并附带到请求中。
- [x] 3.3 更新前端 API client、页面和组件，确保主要功能页面与交互都通过登录态访问。

## 4. 文档、Review、验证与收尾

- [x] 4.1 更新 README 和必要文档，明确 token 登录流程、管理员账号边界与“暂不做注册”的范围。
- [x] 4.2 执行实现自查 / code review，检查安全边界、硬编码范围、无关改动和设计一致性。
- [x] 4.3 运行 OpenSpec 校验、backend 测试、frontend 测试 / 类型检查 / build，并做登录前后 smoke 验证。
- [ ] 4.4 仅在 review 与验证通过后 archive 该 change，并完成 `git add` / `git commit`。
