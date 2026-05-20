# Phase One Architecture Migration

## 当前结论

第一阶段迁移已经从“前后端分离壳层搭好”继续推进到了“根目录遗留运行代码已被清理，后端可在 `backend/` 内独立工作”的状态。

## 已完成

- 建立 `frontend/` 与 `backend/` 两个主工作区
- Flask 后端具备 app factory、统一错误模型、登录鉴权与受保护 API
- Next.js 前端具备登录页、受保护页面、BFF 代理和主要页面壳层
- 回测核心从 repo 根目录收拢到 `backend/backtesting/`
- 因子分析与组合优化模块从 repo 根目录收拢到 `backend/`
- 根目录旧的 Streamlit 页面、调试脚本和过期文档已清理
- `backend/pyproject.toml` 已整理为可同时被 `uv` 和 `Poetry` 消费的配置

## 当前保留的过渡模块

仍然存在但尚未完全 API 化的模块：

- `backend/backtesting/`
- `backend/factor_analysis.py`
- `backend/portfolio_optimizer.py`

这些模块现在都属于后端工作区内部，不再作为 repo 根目录遗留逻辑存在。

## 默认启动流

```text
browser
  -> frontend (Next.js)
  -> frontend route handlers / middleware
  -> backend Flask API
  -> backend services
  -> backend/backtesting and other retained Python modules
```

## 非目标

以下内容不属于当前阶段：

- 恢复旧 Streamlit UI
- 让 repo 根目录继续承载 Python 业务模块
- 将 placeholder 能力误报为已完整迁移

## 下一步建议

1. 为 `factors` / `portfolio` 补真实 API，而不是长期停留在 placeholder。
2. 继续把 `backend/backtesting/` 中更稳定的能力拆进 `backend/app/services/`。
3. 在 CI 中固化 `poetry run pytest`、`poetry run ruff check .`、`npm test` 和 `npm run build`。
