# AKQuant 回测替换 Plan

## 目标

以 `akfamily/akquant` 为唯一主回测内核，替换当前 `backend/backtesting/*` 的主执行职责，并同步升级前后端契约。

## 技术方案

### 依赖与集成

1. 核实 AKQuant 的安装方式、版本锁定与 Python 兼容范围。
2. 在 `backend/pyproject.toml` 中引入 AKQuant 及必要依赖。
3. 建立 `backend/app/services/backtests_akquant.py` 作为整合层。

### 兼容策略

1. 保留现有 `/api/v1/backtests/run` 路由，但内部契约升级为 AKQuant-first。
2. 旧 `backtesting/*` 保留为迁移适配层，逐步下线。
3. 旧自定义策略入口若需保留，则通过 adapter 转换为 AKQuant 支持的策略表达。

### 前端配套

1. 回测 preset 目录、输入字段、执行模式、结果结构全部按 AKQuant 集成结果调整。
2. 结果页支持更丰富的绩效与风险解释。

## 影响文件

- `backend/pyproject.toml`
- `backend/app/services/backtests.py` 或新增 AKQuant service
- `backend/app/schemas/backtests.py`
- `backend/app/api/backtests.py`
- `backend/tests/test_backtests_api.py`
- `frontend/components/backtest-console.tsx`
- `frontend/types/api.ts`

## 风险控制

- 先做隔离 service，不在第一步直接删旧引擎。
- 以回测 contract tests 锁定行为。
- 对 AKQuant 版本做显式 pin，避免未来接口漂移。

## 里程碑

1. 完成依赖评估与引入。
2. 打通最小 AKQuant backend 调用。
3. 对齐前端输入/输出契约。
4. 移除旧引擎主路径。
