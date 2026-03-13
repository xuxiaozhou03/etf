"""绩效指标计算"""

import numpy as np
import pandas as pd
from dataclasses import dataclass

from ...shared.constants import TRADING_DAYS_PER_YEAR, RISK_FREE_RATE


@dataclass
class PerformanceMetrics:
    """绩效指标"""
    # 收益指标
    total_return: float          # 总收益率
    annualized_return: float     # 年化收益率
    cumulative_return: float     # 累计收益率

    # 风险指标
    max_drawdown: float          # 最大回撤
    max_drawdown_duration: int   # 最大回撤持续天数
    annualized_volatility: float # 年化波动率
    downside_volatility: float   # 下行波动率

    # 风险调整收益
    sharpe_ratio: float          # 夏普比率
    sortino_ratio: float         # 索提诺比率
    calmar_ratio: float          # 卡玛比率

    # 交易统计
    total_trades: int            # 总交易次数
    winning_trades: int          # 盈利次数
    losing_trades: int           # 亏损次数
    win_rate: float              # 胜率
    avg_profit: float            # 平均盈利
    avg_loss: float              # 平均亏损
    profit_factor: float         # 盈亏比
    max_consecutive_wins: int    # 最大连续盈利次数
    max_consecutive_losses: int  # 最大连续亏损次数
    avg_holding_days: float      # 平均持仓天数


class MetricsCalculator:
    """绩效指标计算器"""

    def __init__(self, daily_values: list, trades: list):
        """
        Args:
            daily_values: 每日净值列表
            trades: 交易记录列表
        """
        self.daily_values = daily_values
        self.trades = trades

        # 转换为DataFrame
        if daily_values:
            self.df = pd.DataFrame([
                {
                    'date': dv.date,
                    'value': dv.total_value,
                    'return': dv.daily_return,
                }
                for dv in daily_values
            ])
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.set_index('date')
        else:
            self.df = pd.DataFrame()

    def calculate(self) -> PerformanceMetrics:
        """计算所有指标"""
        if self.df.empty:
            return self._empty_metrics()

        returns = self.df['return'].dropna()
        values = self.df['value']

        # 计算各项指标
        total_return = self._total_return()
        annualized_return = self._annualized_return(returns)

        drawdown_info = self._max_drawdown(values)
        max_drawdown = drawdown_info['max_drawdown']
        max_dd_duration = drawdown_info['duration']

        volatility = self._annualized_volatility(returns)
        downside_vol = self._downside_volatility(returns)

        sharpe = self._sharpe_ratio(annualized_return, volatility)
        sortino = self._sortino_ratio(annualized_return, downside_vol)
        calmar = self._calmar_ratio(annualized_return, max_drawdown)

        trade_stats = self._trade_statistics()

        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            cumulative_return=total_return,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            annualized_volatility=volatility,
            downside_volatility=downside_vol,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            **trade_stats
        )

    def _empty_metrics(self) -> PerformanceMetrics:
        """返回空指标"""
        return PerformanceMetrics(
            total_return=0.0,
            annualized_return=0.0,
            cumulative_return=0.0,
            max_drawdown=0.0,
            max_drawdown_duration=0,
            annualized_volatility=0.0,
            downside_volatility=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            avg_profit=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            max_consecutive_wins=0,
            max_consecutive_losses=0,
            avg_holding_days=0.0,
        )

    def _total_return(self) -> float:
        """总收益率"""
        if self.df.empty or len(self.df) < 2:
            return 0.0
        return (self.df['value'].iloc[-1] / self.df['value'].iloc[0]) - 1

    def _annualized_return(self, returns: pd.Series) -> float:
        """年化收益率"""
        if returns.empty:
            return 0.0
        total_days = len(returns)
        if total_days == 0:
            return 0.0
        total_return = (1 + returns).prod() - 1
        return (1 + total_return) ** (TRADING_DAYS_PER_YEAR / total_days) - 1

    def _max_drawdown(self, values: pd.Series) -> dict:
        """最大回撤"""
        if values.empty:
            return {'max_drawdown': 0.0, 'duration': 0}

        cummax = values.cummax()
        drawdown = (values - cummax) / cummax

        max_dd = drawdown.min()

        # 计算最大回撤持续时间
        is_dd = drawdown < 0
        dd_groups = (is_dd != is_dd.shift()).cumsum()

        max_duration = 0
        for _, group in is_dd.groupby(dd_groups):
            if group.any():
                max_duration = max(max_duration, len(group))

        return {
            'max_drawdown': abs(max_dd) if not np.isnan(max_dd) else 0.0,
            'duration': max_duration,
        }

    def _annualized_volatility(self, returns: pd.Series) -> float:
        """年化波动率"""
        if returns.empty or len(returns) < 2:
            return 0.0
        return returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    def _downside_volatility(self, returns: pd.Series) -> float:
        """下行波动率"""
        if returns.empty:
            return 0.0
        negative_returns = returns[returns < 0]
        if negative_returns.empty or len(negative_returns) < 2:
            return 0.0
        return negative_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    def _sharpe_ratio(self, annualized_return: float, volatility: float) -> float:
        """夏普比率"""
        if volatility == 0:
            return 0.0
        return (annualized_return - RISK_FREE_RATE) / volatility

    def _sortino_ratio(self, annualized_return: float, downside_vol: float) -> float:
        """索提诺比率"""
        if downside_vol == 0:
            return 0.0
        return (annualized_return - RISK_FREE_RATE) / downside_vol

    def _calmar_ratio(self, annualized_return: float, max_drawdown: float) -> float:
        """卡玛比率"""
        if max_drawdown == 0:
            return 0.0
        return annualized_return / max_drawdown

    def _trade_statistics(self) -> dict:
        """交易统计"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'avg_holding_days': 0.0,
            }

        # 配对买卖计算盈亏
        profits = []
        holding_days = []

        buys = {}
        for trade in self.trades:
            code = trade.code
            if trade.direction.value == 'buy':
                if code not in buys:
                    buys[code] = []
                buys[code].append(trade)
            else:  # sell
                if code in buys and buys[code]:
                    buy_trade = buys[code].pop(0)
                    profit = (trade.price - buy_trade.price) * trade.shares
                    profits.append(profit)
                    holding_days.append((trade.date - buy_trade.date).days)

        winning = [p for p in profits if p > 0]
        losing = [p for p in profits if p < 0]

        total_trades = len(profits)
        winning_trades = len(winning)
        losing_trades = len(losing)

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0.0,
            'avg_profit': float(np.mean(winning)) if winning else 0.0,
            'avg_loss': float(np.mean(losing)) if losing else 0.0,
            'profit_factor': abs(sum(winning) / sum(losing)) if losing and sum(losing) != 0 else 0.0,
            'max_consecutive_wins': self._max_consecutive([1 if p > 0 else 0 for p in profits], 1),
            'max_consecutive_losses': self._max_consecutive([1 if p < 0 else 0 for p in profits], 1),
            'avg_holding_days': float(np.mean(holding_days)) if holding_days else 0.0,
        }

    def _max_consecutive(self, sequence: list, value: int) -> int:
        """计算最大连续次数"""
        max_count = 0
        current_count = 0

        for item in sequence:
            if item == value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0

        return max_count