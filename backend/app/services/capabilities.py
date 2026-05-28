from __future__ import annotations

CAPABILITIES = [
    {
        "name": "backtest",
        "label": "股票回测",
        "status": "ready",
        "path": "/api/v1/backtests/run",
        "summary": "回测主链路可调用，支持策略预设、执行假设、交易成本、风控参数和结构化结果。",
    },
    {
        "name": "screener",
        "label": "条件选股",
        "status": "ready",
        "path": "/api/v1/screener/run",
        "summary": "选股接口可调用，支持结构化条件、自然语言解释、结果导出与回测交接。",
    },
    {
        "name": "market",
        "label": "行情中心",
        "status": "ready",
        "path": "/api/v1/market",
        "summary": (
            "行情、板块、资讯、情报、预测历史、详情和评估接口均可通过统一接口访问。"
        ),
    },
    {
        "name": "diagnosis",
        "label": "智能诊股",
        "status": "ready",
        "path": "/api/v1/diagnosis/run",
        "summary": "诊股接口可调用，返回行情上下文、指标摘要、结构化诊断段落和风险提示。",
    },
    {
        "name": "factors",
        "label": "因子分析",
        "status": "ready",
        "path": "/api/v1/factors/analyze",
        "summary": "因子接口可调用，返回最新因子、相关性排名与分析窗口。",
    },
    {
        "name": "portfolio",
        "label": "组合优化",
        "status": "ready",
        "path": "/api/v1/portfolio/optimize",
        "summary": "组合接口可调用，返回目标权重、统计指标、优化目标与风险信息。",
    },
    {
        "name": "qa",
        "label": "AI 问答",
        "status": "ready",
        "path": "/api/v1/qa/ask",
        "summary": "输入股票代码和自然语言问题，获取 AI 驱动的分析和回答。",
    },
    {
        "name": "daily",
        "label": "每日复盘",
        "status": "ready",
        "path": "/api/v1/daily/run",
        "summary": "AI 驱动的每日市场分析，包括精选推荐、板块分析和风险提示。",
    },
]


def list_capabilities() -> list[dict[str, str]]:
    return CAPABILITIES


def get_capability(name: str) -> dict[str, str] | None:
    for capability in CAPABILITIES:
        if capability["name"] == name:
            return capability
    return None
