## 1. Dependency And Adapter Setup

- [ ] 1.1 核实 AKQuant 官方依赖、版本锁定与安装方式，并更新 backend 依赖配置。
- [ ] 1.2 建立 AKQuant adapter/service 层，定义请求映射、结果归一化和错误边界。

## 2. Backend Runtime Migration

- [ ] 2.1 将 `POST /api/v1/backtests/run` 改为通过 AKQuant runtime 执行。
- [ ] 2.2 将 `GET /api/v1/backtests/presets` 改为返回 AKQuant-backed 策略目录与参数 metadata。
- [ ] 2.3 为 legacy 字段和必要的自定义策略路径补迁移兼容逻辑。

## 3. Contract And Frontend Alignment

- [ ] 3.1 更新 backtest schema、OpenAPI、前端类型与 API helper，使 contract 与 AKQuant 集成保持一致。
- [ ] 3.2 升级回测工作台页面，支持 AKQuant 参数、结果字段与失败态。

## 4. Legacy Decommissioning And Verification

- [ ] 4.1 将旧 `backend/backtesting/*` 主执行职责降级为兼容层，并规划可删除边界。
- [ ] 4.2 运行后端 contract tests、前端回测页面测试和 OpenSpec 校验，验证 AKQuant 已成为唯一主执行内核。
