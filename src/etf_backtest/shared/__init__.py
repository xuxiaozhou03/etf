"""共享模块"""

from .types import (
    OrderStatus,
    OrderDirection,
    Order,
    Position,
    Trade,
    DailyValue,
    BacktestConfig,
    EtfInfo,
    Kline,
)
from .utils import (
    date_to_str,
    str_to_date,
    get_trading_days,
    format_number,
    format_percent,
    calculate_ma,
    calculate_std,
    calculate_bollinger_bands,
    calculate_max_drawdown,
    round_shares,
)
from .constants import (
    TRADING_DAYS_PER_YEAR,
    RISK_FREE_RATE,
    ETF_CATEGORIES,
    INDEX_CODES,
    INDEX_CODE_MAP,
)
from .exceptions import (
    BacktestError,
    DataError,
    DataNotFoundError,
    StrategyError,
    StrategyNotFoundError,
    OrderError,
    InsufficientFundsError,
    InsufficientSharesError,
    ConfigError,
)

__all__ = [
    # Types
    "OrderStatus",
    "OrderDirection",
    "Order",
    "Position",
    "Trade",
    "DailyValue",
    "BacktestConfig",
    "EtfInfo",
    "Kline",
    # Utils
    "date_to_str",
    "str_to_date",
    "get_trading_days",
    "format_number",
    "format_percent",
    "calculate_ma",
    "calculate_std",
    "calculate_bollinger_bands",
    "calculate_max_drawdown",
    "round_shares",
    # Constants
    "TRADING_DAYS_PER_YEAR",
    "RISK_FREE_RATE",
    "ETF_CATEGORIES",
    "INDEX_CODES",
    "INDEX_CODE_MAP",
    # Exceptions
    "BacktestError",
    "DataError",
    "DataNotFoundError",
    "StrategyError",
    "StrategyNotFoundError",
    "OrderError",
    "InsufficientFundsError",
    "InsufficientSharesError",
    "ConfigError",
]
