## 任务清单

- [x] 1. 补齐 OpenSpec 制品：完成 `design.md`、三份 capability spec 与本任务清单，解除 `phase-one-architecture-migration` 的 apply 阻塞状态。
- [x] 2. 创建 `backend/` Flask 工作区：实现应用工厂、配置、错误处理、CORS、健康检查、能力清单接口和基础蓝图注册。
- [x] 3. 迁移回测主链路到后端：新增回测 request/response schema、后端回测服务适配层、`/api/v1/backtests/run` 接口，并序列化旧回测引擎输出。
- [x] 4. 修正分析类模块的数据契约：让 `factor_analysis.py` 与 `portfolio_optimizer.py` 使用 `HistoricalDataRequest` + `get_ohlcv()`，并在后端暴露对应 skeleton API。
- [x] 5. 创建 `frontend/` Next.js + React 工作区：实现应用壳、导航、API client、首页和回测页面，并为选股、行情、诊股预留占位页面。
- [x] 6. 打通前后端回测链路：前端表单提交到 Flask 回测 API，展示回测指标、资金曲线摘要和最近交易记录。
- [x] 7. 更新工程基线：新增迁移文档、目录结构说明、启动说明、MIT `LICENSE`，并重写根 `README.md` 以默认指向前后端分离模式。
- [x] 8. 完成验证与收尾：运行后端测试/语法检查、前端构建检查，更新 OpenSpec 任务勾选状态，并形成阶段性提交记录。
