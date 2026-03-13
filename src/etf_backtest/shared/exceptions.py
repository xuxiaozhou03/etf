"""异常定义"""


class BacktestError(Exception):
    """回测基础异常"""
    pass


class DataError(BacktestError):
    """数据相关异常"""
    pass


class DataNotFoundError(DataError):
    """数据未找到"""
    pass


class StrategyError(BacktestError):
    """策略相关异常"""
    pass


class StrategyNotFoundError(StrategyError):
    """策略未找到"""
    pass


class OrderError(BacktestError):
    """订单相关异常"""
    pass


class InsufficientFundsError(OrderError):
    """资金不足"""
    pass


class InsufficientSharesError(OrderError):
    """持仓不足"""
    pass


class LimitUpError(OrderError):
    """涨停无法买入"""
    pass


class LimitDownError(OrderError):
    """跌停无法卖出"""
    pass


class ConfigError(BacktestError):
    """配置相关异常"""
    pass
