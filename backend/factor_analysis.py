"""
因子分析模块
"""
from typing import Dict, List

import pandas as pd

from backtesting.data import HistoricalDataRequest, SmartDataProvider


class FactorAnalyzer:
    """因子分析器"""

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

    def calculate_factors(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        计算多个技术因子

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含各因子的DataFrame
        """
        # 获取数据
        df = self._get_history(symbol, start_date, end_date)

        if df.empty:
            return pd.DataFrame()

        # 计算各类因子
        factors = pd.DataFrame(index=df.index)

        # 1. 动量因子
        factors['momentum_5'] = df['close'].pct_change(5)  # 5日动量
        factors['momentum_10'] = df['close'].pct_change(10)  # 10日动量
        factors['momentum_20'] = df['close'].pct_change(20)  # 20日动量

        # 2. 反转因子
        factors['reversal_5'] = -df['close'].pct_change(5)  # 5日反转
        factors['reversal_10'] = -df['close'].pct_change(10)  # 10日反转

        # 3. 波动率因子
        factors['volatility_10'] = df['close'].pct_change().rolling(10).std()  # 10日波动率
        factors['volatility_20'] = df['close'].pct_change().rolling(20).std()  # 20日波动率

        # 4. 成交量因子
        factors['volume_ratio_5'] = df['volume'] / df['volume'].rolling(5).mean()  # 5日量比
        factors['volume_ratio_10'] = df['volume'] / df['volume'].rolling(10).mean()  # 10日量比

        # 5. 价格位置因子
        rolling_min = df['close'].rolling(20).min()
        rolling_max = df['close'].rolling(20).max()
        factors['price_position_20'] = (df['close'] - rolling_min) / (rolling_max - rolling_min)

        # 6. 均线因子
        ma5 = df['close'].rolling(5).mean()
        ma10 = df['close'].rolling(10).mean()
        ma20 = df['close'].rolling(20).mean()

        factors['ma_cross_5_10'] = (ma5 - ma10) / ma10  # 5日均线与10日均线的偏离度
        factors['ma_cross_5_20'] = (ma5 - ma20) / ma20  # 5日均线与20日均线的偏离度
        factors['price_to_ma20'] = (df['close'] - ma20) / ma20  # 价格与20日均线的偏离度

        # 7. 振幅因子
        factors['amplitude_5'] = (df['high'].rolling(5).max() - df['low'].rolling(5).min()) / \
                                 df['close'].rolling(5).mean()

        # 8. 资金流向因子（简化版）
        factors['money_flow'] = df['close'].pct_change() * df['volume']

        # 填充缺失值
        factors = factors.fillna(0)

        return factors

    def analyze_factor_performance(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        forward_days: int = 5
    ) -> Dict[str, float]:
        """
        分析各因子的预测能力

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            forward_days: 前瞻收益天数

        Returns:
            各因子的IC值（信息系数）
        """
        # 获取因子数据
        factors = self.calculate_factors(symbol, start_date, end_date)

        if factors.empty:
            return {}

        # 获取价格数据计算未来收益
        df = self._get_history(symbol, start_date, end_date)
        forward_return = df['close'].pct_change(forward_days).shift(-forward_days)

        # 计算每个因子与未来收益的相关性（IC值）
        ic_values = {}
        for factor_name in factors.columns:
            # 计算Spearman相关系数（秩相关）
            valid_data = pd.DataFrame({
                'factor': factors[factor_name],
                'return': forward_return
            }).dropna()

            if len(valid_data) > 10:  # 至少需要10个有效数据点
                ic = valid_data['factor'].corr(valid_data['return'], method='spearman')
                ic_values[factor_name] = ic
            else:
                ic_values[factor_name] = 0.0

        return ic_values

    def get_factor_summary(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取多只股票的因子汇总

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            因子汇总DataFrame
        """
        summary_data = []

        for symbol in symbols:
            try:
                ic_values = self.analyze_factor_performance(symbol, start_date, end_date)

                if ic_values:
                    row = {'股票代码': symbol}
                    row.update(ic_values)
                    summary_data.append(row)
            except Exception as e:
                print(f"分析 {symbol} 时出错: {e}")
                continue

        if not summary_data:
            return pd.DataFrame()

        df = pd.DataFrame(summary_data)
        return df

    def select_top_factors(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        top_n: int = 5
    ) -> List[str]:
        """
        选择表现最好的N个因子

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            top_n: 选择因子数量

        Returns:
            因子名称列表
        """
        ic_values = self.analyze_factor_performance(symbol, start_date, end_date)

        if not ic_values:
            return []

        # 按IC绝对值排序
        sorted_factors = sorted(ic_values.items(), key=lambda x: abs(x[1]), reverse=True)

        return [factor[0] for factor in sorted_factors[:top_n]]
