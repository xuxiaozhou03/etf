"""工具函数"""

from datetime import datetime, date, timedelta
from typing import Optional
import pandas as pd


def date_to_str(d: date | datetime) -> str:
    """日期转字符串"""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    return d.strftime("%Y-%m-%d")


def str_to_date(s: str) -> date:
    """字符串转日期"""
    return datetime.strptime(s, "%Y-%m-%d").date()


def get_trading_days(start: date, end: date) -> list[date]:
    """获取交易日列表（简化版，排除周末）"""
    days = []
    current = start
    while current <= end:
        # 排除周末
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def format_number(value: float, decimal: int = 2) -> str:
    """格式化数字"""
    if abs(value) >= 1e8:
        return f"{value / 1e8:.{decimal}f}亿"
    elif abs(value) >= 1e4:
        return f"{value / 1e4:.{decimal}f}万"
    else:
        return f"{value:.{decimal}f}"


def format_percent(value: float, decimal: int = 2) -> str:
    """格式化百分比"""
    return f"{value * 100:.{decimal}f}%"


def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
    """计算移动平均线"""
    return prices.rolling(window=period).mean()


def calculate_std(prices: pd.Series, period: int) -> pd.Series:
    """计算标准差"""
    return prices.rolling(window=period).std()


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带

    Returns:
        (upper, middle, lower)
    """
    middle = calculate_ma(prices, period)
    std = calculate_std(prices, period)
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def calculate_max_drawdown(values: pd.Series) -> tuple[float, int]:
    """
    计算最大回撤

    Returns:
        (最大回撤率, 持续天数)
    """
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

    return abs(max_dd), max_duration


def round_shares(shares: int) -> int:
    """将股数取整到100的倍数"""
    return (shares // 100) * 100
