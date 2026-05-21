from __future__ import annotations

CAPABILITIES = [
    {
        "name": "backtest",
        "label": "股票回测",
        "status": "migrated",
        "path": "/api/v1/backtests/run",
        "summary": "已迁通 AKQuant-backed 回测主链路，可从前端调用 Flask API 执行结构化回测。",
    },
    {
        "name": "screener",
        "label": "条件选股",
        "status": "migrated",
        "path": "/api/v1/screener/run",
        "summary": "已提供结构化条件、自然语言解释、结果导出与回测回灌契约。",
    },
    {
        "name": "market",
        "label": "行情中心",
        "status": "migrated",
        "path": "/api/v1/market",
        "summary": (
            "已提供 backend 侧 AkShare 市场数据与 Jin10 新闻 intelligence API，"
            "前端深度页面仍待继续迁移。"
        ),
    },
    {
        "name": "diagnosis",
        "label": "AI 诊股",
        "status": "migrated",
        "path": "/api/v1/diagnosis/run",
        "summary": "已提供行情上下文、指标摘要、结构化诊断报告与降级 metadata。",
    },
    {
        "name": "factors",
        "label": "因子分析",
        "status": "migrated",
        "path": "/api/v1/factors/analyze",
        "summary": "已封装保留因子模块为正式 API，返回最新因子、IC 排名与分析窗口。",
    },
    {
        "name": "portfolio",
        "label": "组合优化",
        "status": "migrated",
        "path": "/api/v1/portfolio/optimize",
        "summary": "已封装组合优化模块为正式 API，返回权重、统计指标与优化 metadata。",
    },
]


def list_capabilities() -> list[dict[str, str]]:
    return CAPABILITIES


def get_capability(name: str) -> dict[str, str] | None:
    for capability in CAPABILITIES:
        if capability["name"] == name:
            return capability
    return None
