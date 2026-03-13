"""数据缓存"""

import hashlib
import time
from pathlib import Path
from typing import Any, Callable
from functools import wraps

import joblib
import pandas as pd

from config import get_logger

logger = get_logger(__name__)


class DataCache:
    """数据缓存管理器"""

    def __init__(
        self,
        cache_dir: str | Path = "./data/cache",
        expire_hours: int = 24,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.expire_hours = expire_hours

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"

    def get(self, key: str) -> Any | None:
        """获取缓存"""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        # 检查过期
        file_mtime = cache_path.stat().st_mtime
        if time.time() - file_mtime > self.expire_hours * 3600:
            cache_path.unlink()
            return None

        try:
            return joblib.load(cache_path)
        except Exception as e:
            logger.warning(f"读取缓存失败: {key}, {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        cache_path = self._get_cache_path(key)
        try:
            joblib.dump(value, cache_path)
        except Exception as e:
            logger.warning(f"写入缓存失败: {key}, {e}")

    def delete(self, key: str) -> None:
        """删除缓存"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()

    def clear(self) -> None:
        """清空所有缓存"""
        for f in self.cache_dir.glob("*.pkl"):
            f.unlink()

    def clear_expired(self) -> int:
        """清理过期缓存"""
        count = 0
        for f in self.cache_dir.glob("*.pkl"):
            if time.time() - f.stat().st_mtime > self.expire_hours * 3600:
                f.unlink()
                count += 1
        return count


class KlineCache:
    """K线数据缓存"""

    def __init__(self, cache_dir: str | Path = "./data/cache/klines"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_klines(self, code: str) -> pd.DataFrame | None:
        """获取缓存的K线数据"""
        cache_file = self.cache_dir / f"{code}.parquet"

        if not cache_file.exists():
            return None

        try:
            return pd.read_parquet(cache_file)
        except Exception as e:
            logger.warning(f"读取K线缓存失败: {code}, {e}")
            return None

    def set_klines(self, code: str, df: pd.DataFrame) -> None:
        """保存K线数据到缓存"""
        cache_file = self.cache_dir / f"{code}.parquet"

        try:
            df.to_parquet(cache_file)
        except Exception as e:
            logger.warning(f"写入K线缓存失败: {code}, {e}")

    def get_kline_last_date(self, code: str) -> str | None:
        """获取缓存中K线的最后日期"""
        df = self.get_klines(code)
        if df is None or df.empty:
            return None

        try:
            # 获取最后一个日期
            if isinstance(df.index, pd.MultiIndex):
                dates = df.index.get_level_values("date")
            else:
                dates = df.index

            return dates.max().strftime("%Y-%m-%d")
        except Exception:
            return None


def cached(cache_key_func: Callable[..., str]):
    """
    缓存装饰器

    Args:
        cache_key_func: 生成缓存键的函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 检查是否有缓存实例
            cache = getattr(self, "_cache", None)
            if cache is None:
                return await func(self, *args, **kwargs)

            # 生成缓存键
            key = cache_key_func(*args, **kwargs)

            # 尝试从缓存获取
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {key}")
                return cached_value

            # 执行函数
            result = await func(self, *args, **kwargs)

            # 存入缓存
            cache.set(key, result)

            return result

        return wrapper
    return decorator
