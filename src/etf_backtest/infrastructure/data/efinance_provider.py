"""基于 efinance 的数据提供者"""

import asyncio
from datetime import date, datetime
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np

from .provider import DataProvider
from ...shared.constants import INDEX_CODE_MAP
from ...shared.exceptions import DataError, DataNotFoundError
from config import get_logger

logger = get_logger(__name__)


class EfinanceProvider(DataProvider):
    """基于 efinance 的数据提供者"""

    def __init__(
        self,
        cache_dir: str | Path = "./data/cache",
        request_delay: float = 0.2,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.request_delay = request_delay
        self._last_request_time: float = 0

    def _normalize_etf_list(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化ETF列表"""
        if df is None or df.empty:
            return pd.DataFrame(columns=[
                "code", "name", "type", "category", "benchmark", "tracking", "asset_size"
            ])

        result = pd.DataFrame()
        result["code"] = df.get("代码", df.get("code", ""))
        result["name"] = df.get("名称", df.get("name", ""))
        result["type"] = 0  # 默认上证
        result["category"] = ""
        result["benchmark"] = ""
        result["tracking"] = ""
        result["asset_size"] = 0.0

        return result

    def _normalize_klines(self, df: pd.DataFrame, code: str) -> pd.DataFrame:
        """标准化K线数据"""
        if df is None or df.empty:
            return pd.DataFrame(columns=[
                "open", "high", "low", "close", "volume", "amount", "turnover_rate", "change_pct"
            ])

        # efinance 返回的列名
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

        # 确保日期列存在
        if "date" not in df.columns:
            df["date"] = pd.date_range(end=date.today(), periods=len(df))

        df["date"] = pd.to_datetime(df["date"])
        df["code"] = code

        # 设置索引
        df = df.set_index(["code", "date"])

        # 确保所有列存在
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
            import efinance as ef

            await self._rate_limit()

            # 获取ETF列表
            # 注意：efinance 的 ETF 列表获取方式可能需要调整
            try:
                df = ef.stock.get_quote_history("ETF")
            except Exception:
                # 备用方案：手动构建列表
                df = pd.DataFrame()

            return self._normalize_etf_list(df)

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
            import efinance as ef

            await self._rate_limit()

            # 格式化日期
            start = start_date.strftime("%Y%m%d") if start_date else "19900101"
            end = end_date.strftime("%Y%m%d") if end_date else date.today().strftime("%Y%m%d")

            logger.info(f"获取K线数据: {code}, {start} ~ {end}")

            # 使用 efinance 获取 K 线
            df = ef.stock.get_quote_history(
                code,
                beg=start,
                end=end,
                klt=101,  # 日K
                fqt=1,    # 前复权
            )

            if df is None or df.empty:
                raise DataNotFoundError(f"未找到 {code} 的K线数据")

            return self._normalize_klines(df, code)

        except DataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取K线数据失败: {code}, {e}")
            raise DataError(f"获取K线数据失败: {e}")

    async def get_realtime_quote(self, codes: list[str]) -> pd.DataFrame:
        """获取实时行情"""
        try:
            import efinance as ef

            results = []
            for code in codes:
                await self._rate_limit()
                try:
                    quote = ef.stock.get_realtime_quotes([code])
                    if quote is not None and not quote.empty:
                        results.append(quote)
                except Exception as e:
                    logger.warning(f"获取 {code} 实时行情失败: {e}")
                    continue

            if not results:
                return pd.DataFrame()

            df = pd.concat(results, ignore_index=True)

            # 标准化列名
            column_map = {
                "代码": "code",
                "名称": "name",
                "最新价": "price",
                "涨跌幅": "change_pct",
                "成交量": "volume",
                "成交额": "amount",
            }
            df = df.rename(columns=column_map)

            return df

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
            import efinance as ef

            await self._rate_limit()

            # 转换指数代码
            actual_code = INDEX_CODE_MAP.get(code, code)

            start = start_date.strftime("%Y%m%d") if start_date else "19900101"
            end = end_date.strftime("%Y%m%d") if end_date else date.today().strftime("%Y%m%d")

            logger.info(f"获取指数K线: {actual_code}, {start} ~ {end}")

            df = ef.stock.get_quote_history(
                actual_code,
                beg=start,
                end=end,
                klt=101,
                fqt=1,
            )

            if df is None or df.empty:
                raise DataNotFoundError(f"未找到指数 {code} 的K线数据")

            return self._normalize_klines(df, code)

        except DataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取指数K线失败: {code}, {e}")
            raise DataError(f"获取指数K线失败: {e}")
