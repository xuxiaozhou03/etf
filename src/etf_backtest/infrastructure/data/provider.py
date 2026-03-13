"""数据提供者抽象基类"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol, runtime_checkable
import pandas as pd


@runtime_checkable
class KlineData(Protocol):
    """K线数据协议"""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float


class DataProvider(ABC):
    """数据提供者抽象基类"""

    @abstractmethod
    async def get_etf_list(self) -> pd.DataFrame:
        """
        获取ETF列表

        Returns:
            DataFrame with columns: code, name, type, category, benchmark, tracking, asset_size
        """
        pass

    @abstractmethod
    async def get_klines(
        self,
        code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        """
        获取K线数据

        Args:
            code: ETF代码
            start_date: 起始日期
            end_date: 结束日期

        Returns:
            DataFrame with MultiIndex(code, date) and columns: open, high, low, close, volume, amount
        """
        pass

    @abstractmethod
    async def get_realtime_quote(self, codes: list[str]) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            codes: ETF代码列表

        Returns:
            DataFrame with columns: code, name, price, change_pct, volume, amount
        """
        pass

    @abstractmethod
    async def get_index_klines(
        self,
        code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        """
        获取指数K线数据

        Args:
            code: 指数代码
            start_date: 起始日期
            end_date: 结束日期

        Returns:
            DataFrame with MultiIndex(code, date) and columns: open, high, low, close, volume, amount
        """
        pass
