"""基于 akshare 的数据提供者"""

import asyncio
from datetime import date
from pathlib import Path
import pandas as pd
import numpy as np

from .provider import DataProvider
from ...shared.constants import INDEX_CODE_MAP
from ...shared.exceptions import DataError, DataNotFoundError
from config import get_logger

logger = get_logger(__name__)


class AkshareProvider(DataProvider):
    """基于 akshare 的数据提供者"""

    def __init__(
        self,
        cache_dir: str | Path = "./data/cache",
        request_delay: float = 0.3,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.request_delay = request_delay
        self._last_request_time: float = 0

    def _normalize_klines(self, df: pd.DataFrame, code: str) -> pd.DataFrame:
        """标准化K线数据"""
        if df is None or df.empty:
            return pd.DataFrame(columns=[
                "open", "high", "low", "close", "volume", "amount", "turnover_rate", "change_pct"
            ])

        # akshare 返回的列名
        column_map = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "换手率": "turnover_rate",
            "涨跌幅": "change_pct",
        }

        df = df.rename(columns=column_map)

        if "date" not in df.columns:
            df["date"] = pd.date_range(end=date.today(), periods=len(df))

        df["date"] = pd.to_datetime(df["date"])
        df["code"] = code

        df = df.set_index(["code", "date"])

        for col in ["open", "high", "low", "close", "volume", "amount", "turnover_rate", "change_pct"]:
            if col not in df.columns:
                df[col] = np.nan

        return df

    async def _rate_limit(self) -> None:
        """请求限流"""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            await asyncio.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

    async def get_etf_list(self) -> pd.DataFrame:
        """获取ETF列表"""
        try:
            import akshare as ak

            await self._rate_limit()

            # 获取ETF列表
            df = ak.fund_etf_category_sina(symbol="ETF基金")

            result = pd.DataFrame()
            result["code"] = df.get("代码", "")
            result["name"] = df.get("名称", "")
            result["type"] = 0
            result["category"] = ""
            result["benchmark"] = ""
            result["tracking"] = ""
            result["asset_size"] = 0.0

            return result

        except Exception as e:
            logger.error(f"获取ETF列表失败: {e}")
            raise DataError(f"获取ETF列表失败: {e}")

    async def get_klines(
        self,
        code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        """获取K线数据"""
        try:
            import akshare as ak

            await self._rate_limit()

            logger.info(f"获取K线数据: {code}, {start_date} ~ {end_date}")

            # 使用 akshare 获取 ETF K 线
            df = ak.fund_etf_hist_sina(symbol=code)

            if df is None or df.empty:
                raise DataNotFoundError(f"未找到 {code} 的K线数据")

            # 过滤日期范围
            if start_date:
                df = df[df["日期"] >= start_date.strftime("%Y-%m-%d")]
            if end_date:
                df = df[df["日期"] <= end_date.strftime("%Y-%m-%d")]

            return self._normalize_klines(df, code)

        except DataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取K线数据失败: {code}, {e}")
            raise DataError(f"获取K线数据失败: {e}")

    async def get_realtime_quote(self, codes: list[str]) -> pd.DataFrame:
        """获取实时行情"""
        try:
            import akshare as ak

            await self._rate_limit()

            df = ak.fund_etf_spot_em()

            # 过滤指定代码
            if codes:
                df = df[df["代码"].isin(codes)]

            result = pd.DataFrame()
            result["code"] = df["代码"]
            result["name"] = df["名称"]
            result["price"] = df["最新价"]
            result["change_pct"] = df["涨跌幅"]
            result["volume"] = df["成交量"]
            result["amount"] = df["成交额"]

            return result

        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            raise DataError(f"获取实时行情失败: {e}")

    async def get_index_klines(
        self,
        code: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        """获取指数K线数据"""
        try:
            import akshare as ak

            await self._rate_limit()

            # 转换指数代码
            actual_code = INDEX_CODE_MAP.get(code, code)

            logger.info(f"获取指数K线: {actual_code}")

            # akshare 获取指数
            df = ak.stock_zh_index_daily(symbol=actual_code)

            if df is None or df.empty:
                raise DataNotFoundError(f"未找到指数 {code} 的K线数据")

            # 过滤日期范围
            if start_date:
                df = df[df["date"] >= start_date.strftime("%Y-%m-%d")]
            if end_date:
                df = df[df["date"] <= end_date.strftime("%Y-%m-%d")]

            return self._normalize_klines(df, code)

        except DataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取指数K线失败: {code}, {e}")
            raise DataError(f"获取指数K线失败: {e}")
