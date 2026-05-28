from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from .market_data import AkshareMarketDataService
from .stock_detail import StockDetailService
from .deepseek_prediction import DeepSeekMarketPredictionService
from .runtime_cache import TTLCache

CHINA_TIMEZONE = timezone(timedelta(hours=8))

REPORT_SYSTEM_PROMPT = """你是 A 股市场每日复盘分析师。
根据提供的市场数据和筛选结果，生成结构化的每日研究报告。

报告结构：
1. 市场总结 - 大盘走势、成交量变化、市场情绪
2. 精选推荐 - 基于技术指标筛选的个股推荐，包含推荐理由
3. 板块分析 - 热门板块轮动分析
4. 风险提示 - 当前市场风险因素

规则：
- 所有文本使用简体中文
- 基于数据说话，不编造数据
- 不给出买入建议，只做研究分析
- 结尾提醒："以上分析仅供参考，不构成投资建议。"

返回 JSON 格式：
{
  "marketSummary": "市场总结文字",
  "topPicks": [{"symbol": "000001", "name": "平安银行", "reason": "推荐理由", "confidence": 0.7}],
  "sectorAnalysis": "板块分析文字",
  "riskWarnings": ["风险提示1", "风险提示2"],
  "summary": "一句话总结"
}
"""

class DailyAnalysisService:
    def __init__(
        self,
        market_data_service: AkshareMarketDataService | None = None,
        stock_detail_service: StockDetailService | None = None,
        deepseek_service: DeepSeekMarketPredictionService | None = None,
        storage_path: Path | None = None,
    ):
        self.market_data_service = market_data_service or AkshareMarketDataService()
        self.stock_detail_service = stock_detail_service or StockDetailService()
        self.deepseek_service = deepseek_service
        self.storage_path = storage_path or Path("instance") / "daily_reports.jsonl"
        self._cache = TTLCache(300)

    def run_daily_screen(self, universe: list[str] | None = None) -> dict[str, Any]:
        """Run multi-indicator composite screening."""
        if universe is None:
            universe = ["000001", "600000", "300750", "000858", "601318", "000002", "600519", "002594", "601012", "600036"]

        candidates = []
        for symbol in universe[:20]:
            try:
                detail = self.stock_detail_service.get_stock_detail(symbol)
                if detail.get("error"):
                    continue

                score = 0.0
                reasons = []

                price = detail.get("price") or 0
                change = detail.get("changePercent") or 0
                turnover = detail.get("turnoverRate") or 0
                volume_ratio = detail.get("volumeRatio") or 1
                pe = detail.get("pe") or 0

                if change > 0:
                    score += min(change / 5, 1.0) * 2
                    reasons.append(f"涨跌幅 {change:.2f}%")

                if volume_ratio > 1.5:
                    score += min((volume_ratio - 1) / 2, 1.0) * 2
                    reasons.append(f"量比 {volume_ratio:.2f}")

                if 2 < turnover < 10:
                    score += 1
                    reasons.append(f"换手率 {turnover:.2f}%")

                if 0 < pe < 30:
                    score += 1
                    reasons.append(f"PE {pe:.1f} 估值合理")

                if score > 2:
                    candidates.append({
                        "symbol": symbol.zfill(6),
                        "name": detail.get("name", symbol),
                        "price": price,
                        "changePercent": change,
                        "score": round(score, 2),
                        "reasons": reasons,
                        "industry": detail.get("industry", ""),
                    })
            except Exception:
                continue

        candidates.sort(key=lambda x: x["score"], reverse=True)

        return {
            "candidates": candidates[:10],
            "totalScreened": len(universe),
            "timestamp": datetime.now(CHINA_TIMEZONE).isoformat(),
        }

    def generate_report(self, screen_results: dict[str, Any]) -> dict[str, Any]:
        """Generate AI-powered daily report."""
        candidates = screen_results.get("candidates", [])

        if not self.deepseek_service or not self.deepseek_service.api_key:
            return self._build_fallback_report(screen_results)

        try:
            context_parts = ["今日筛选结果："]
            for c in candidates[:10]:
                context_parts.append(
                    f"- {c['name']}（{c['symbol']}）价格 {c['price']}，"
                    f"涨跌 {c['changePercent']:.2f}%，"
                    f"综合评分 {c['score']}，"
                    f"理由：{', '.join(c['reasons'])}"
                )

            context = "\n".join(context_parts)

            url = f"{self.deepseek_service.base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_service.api_key}",
            }
            payload = {
                "model": self.deepseek_service.model,
                "messages": [
                    {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                "temperature": 0.5,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"},
            }

            response = self.deepseek_service.session.post(
                url, json=payload, headers=headers, timeout=60
            )
            response.raise_for_status()
            data = response.json()

            content = ""
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")

            report_data = json.loads(content) if content else {}
        except Exception:
            report_data = {}

        report = {
            "date": datetime.now(CHINA_TIMEZONE).strftime("%Y-%m-%d"),
            "marketSummary": report_data.get("marketSummary", "市场数据获取中..."),
            "topPicks": report_data.get("topPicks", candidates[:5]),
            "sectorAnalysis": report_data.get("sectorAnalysis", "板块分析中..."),
            "riskWarnings": report_data.get("riskWarnings", ["市场有风险，投资需谨慎。"]),
            "summary": report_data.get("summary", ""),
            "screenResults": screen_results,
            "generatedAt": datetime.now(CHINA_TIMEZONE).isoformat(),
            "degraded": False,
        }

        self._save_report(report)
        return report

    def get_latest_report(self) -> dict[str, Any] | None:
        """Get the most recent daily report."""
        reports = self._load_reports()
        return reports[-1] if reports else None

    def get_report_history(self, limit: int = 30) -> list[dict[str, Any]]:
        """Get historical reports."""
        reports = self._load_reports()
        return reports[-limit:]

    def _build_fallback_report(self, screen_results: dict[str, Any]) -> dict[str, Any]:
        candidates = screen_results.get("candidates", [])
        return {
            "date": datetime.now(CHINA_TIMEZONE).strftime("%Y-%m-%d"),
            "marketSummary": f"今日共筛选 {screen_results.get('totalScreened', 0)} 只股票，"
                           f"其中 {len(candidates)} 只进入候选池。",
            "topPicks": candidates[:5],
            "sectorAnalysis": "需要配置 DEEPSEEK_API_KEY 以获取 AI 板块分析。",
            "riskWarnings": ["以上分析仅供参考，不构成投资建议。"],
            "summary": f"筛选出 {len(candidates)} 只候选股票。",
            "screenResults": screen_results,
            "generatedAt": datetime.now(CHINA_TIMEZONE).isoformat(),
            "degraded": True,
        }

    def _save_report(self, report: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(report, ensure_ascii=False) + "\n")

    def _load_reports(self) -> list[dict[str, Any]]:
        if not self.storage_path.exists():
            return []
        reports = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        reports.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return reports
