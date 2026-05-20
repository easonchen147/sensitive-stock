"""
组合优化模块
"""
from typing import Dict, List

import numpy as np
import pandas as pd

from backtesting.data import HistoricalDataRequest, SmartDataProvider


class PortfolioOptimizer:
    """投资组合优化器"""

    def __init__(self):
        self.data_provider = SmartDataProvider()

    def _get_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return self.data_provider.get_ohlcv(
            HistoricalDataRequest(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
        )

    def calculate_returns(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        计算多只股票的收益率

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            收益率DataFrame
        """
        returns_dict = {}

        for symbol in symbols:
            try:
                df = self._get_history(symbol, start_date, end_date)
                if not df.empty:
                    returns_dict[symbol] = df['close'].pct_change()
            except Exception as e:
                print(f"获取 {symbol} 数据失败: {e}")
                continue

        if not returns_dict:
            return pd.DataFrame()

        returns_df = pd.DataFrame(returns_dict)
        return returns_df.dropna()

    def calculate_covariance_matrix(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        计算协方差矩阵

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            协方差矩阵
        """
        returns = self.calculate_returns(symbols, start_date, end_date)

        if returns.empty:
            return pd.DataFrame()

        # 年化协方差矩阵（假设252个交易日）
        cov_matrix = returns.cov() * 252

        return cov_matrix

    def equal_weight_portfolio(self, symbols: List[str]) -> Dict[str, float]:
        """
        等权重组合

        Args:
            symbols: 股票代码列表

        Returns:
            权重字典
        """
        n = len(symbols)
        weight = 1.0 / n

        return {symbol: weight for symbol in symbols}

    def minimum_variance_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, float]:
        """
        最小方差组合

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            权重字典
        """
        cov_matrix = self.calculate_covariance_matrix(symbols, start_date, end_date)

        if cov_matrix.empty:
            return self.equal_weight_portfolio(symbols)

        try:
            # 计算协方差矩阵的逆
            inv_cov = np.linalg.inv(cov_matrix.values)

            # 单位向量
            ones = np.ones(len(symbols))

            # 最小方差组合权重
            weights = inv_cov @ ones / (ones @ inv_cov @ ones)

            # 确保权重为正且和为1
            weights = np.maximum(weights, 0)
            weights = weights / weights.sum()

            return {symbol: weight for symbol, weight in zip(symbols, weights, strict=False)}

        except np.linalg.LinAlgError:
            # 如果矩阵不可逆，返回等权重
            return self.equal_weight_portfolio(symbols)

    def maximum_sharpe_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        risk_free_rate: float = 0.03
    ) -> Dict[str, float]:
        """
        最大夏普比率组合（简化版）

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            risk_free_rate: 无风险利率

        Returns:
            权重字典
        """
        returns = self.calculate_returns(symbols, start_date, end_date)

        if returns.empty:
            return self.equal_weight_portfolio(symbols)

        # 计算年化收益率
        mean_returns = returns.mean() * 252

        # 计算协方差矩阵
        cov_matrix = returns.cov() * 252

        try:
            # 简化的最大夏普比率优化
            # 使用均值-方差优化的解析解

            inv_cov = np.linalg.inv(cov_matrix.values)
            excess_returns = mean_returns.values - risk_free_rate

            # 最优权重
            weights = inv_cov @ excess_returns
            weights = np.maximum(weights, 0)  # 不允许做空
            weights = weights / weights.sum()

            return {symbol: weight for symbol, weight in zip(symbols, weights, strict=False)}

        except (np.linalg.LinAlgError, ValueError):
            return self.equal_weight_portfolio(symbols)

    def risk_parity_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, float]:
        """
        风险平价组合

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            权重字典
        """
        returns = self.calculate_returns(symbols, start_date, end_date)

        if returns.empty:
            return self.equal_weight_portfolio(symbols)

        # 计算波动率
        volatilities = returns.std() * np.sqrt(252)

        # 风险平价：权重与波动率成反比
        inv_vol = 1.0 / volatilities
        weights = inv_vol / inv_vol.sum()

        return {symbol: weight for symbol, weight in zip(symbols, weights.values, strict=False)}

    def calculate_portfolio_metrics(
        self,
        symbols: List[str],
        weights: Dict[str, float],
        start_date: str,
        end_date: str
    ) -> Dict[str, float]:
        """
        计算组合指标

        Args:
            symbols: 股票代码列表
            weights: 权重字典
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            组合指标字典
        """
        returns = self.calculate_returns(symbols, start_date, end_date)

        if returns.empty:
            return {}

        # 计算组合收益率
        weight_array = np.array([weights.get(symbol, 0) for symbol in returns.columns])
        portfolio_returns = (returns * weight_array).sum(axis=1)

        # 计算指标
        total_return = (1 + portfolio_returns).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0

        # 最大回撤
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        return {
            '总收益率': total_return,
            '年化收益率': annual_return,
            '年化波动率': volatility,
            '夏普比率': sharpe_ratio,
            '最大回撤': max_drawdown
        }

    def compare_strategies(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        比较不同组合策略

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            比较结果DataFrame
        """
        strategies = {
            '等权重': self.equal_weight_portfolio(symbols),
            '最小方差': self.minimum_variance_portfolio(symbols, start_date, end_date),
            '最大夏普': self.maximum_sharpe_portfolio(symbols, start_date, end_date),
            '风险平价': self.risk_parity_portfolio(symbols, start_date, end_date)
        }

        results = []

        for strategy_name, weights in strategies.items():
            metrics = self.calculate_portfolio_metrics(symbols, weights, start_date, end_date)

            if metrics:
                row = {'策略': strategy_name}
                row.update(metrics)

                # 添加权重信息
                for symbol in symbols:
                    row[f'{symbol}_权重'] = weights.get(symbol, 0)

                results.append(row)

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df
