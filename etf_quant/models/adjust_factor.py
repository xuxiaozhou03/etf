"""复权因子表：schema + 读写 + 前复权系数计算。"""

from __future__ import annotations

import sqlite3
from typing import List

import numpy as np
import pandas as pd

from etf_quant.models.base import ColumnDef, Model


class AdjustFactor(Model):
    """复权因子（分红日记录，date 为 YYYYMMDD 整数格式）。"""

    table = "adjust_factors"
    columns: List[ColumnDef] = [
        ("code", "TEXT", "NOT NULL"),
        ("date", "TEXT", "NOT NULL"),
        ("factor", "REAL", ""),
    ]
    primary_keys: List[str] = ["code", "date"]

    @classmethod
    def upsert(cls, conn: sqlite3.Connection, code: str, factors: List[List]) -> int:
        """写入复权因子（factors: [[date_int, factor], ...]）。"""
        if not factors:
            return 0
        sql = cls.upsert_sql()
        values = [(code, str(f[0]), float(f[1])) for f in factors]
        conn.executemany(sql, values)
        conn.commit()
        return len(values)

    @classmethod
    def load(cls, conn: sqlite3.Connection, code: str) -> List[List]:
        """复权因子 [[date_int, factor], ...]，按日期升序。"""
        rows = conn.execute(
            f"SELECT date, factor FROM {cls.table} WHERE code=? ORDER BY date", (code,)
        ).fetchall()
        return [[r[0], r[1]] for r in rows]

    @staticmethod
    def cumulative_factor(dates: pd.Series, factors: List[List]) -> pd.Series:
        """前复权累计系数：adj_price = price / cum_factor。

        cum_factor(交易日 t) = t 之后所有除权日 factor 的乘积（无后续除权则为 1）。
        假设复权因子为"除权日事件系数"，对历史价做后缀累积积恢复前复权。
        """
        if not factors:
            return pd.Series(1.0, index=dates.index)
        fdf = pd.DataFrame(factors, columns=["date", "factor"])
        fdf["date"] = pd.to_datetime(fdf["date"].astype(str), format="%Y%m%d")
        fdf = fdf.sort_values("date").reset_index(drop=True)
        suffix = fdf["factor"].iloc[::-1].cumprod().iloc[::-1].to_numpy()
        idx = np.searchsorted(fdf["date"].to_numpy(), dates.to_numpy(), side="right")
        out = np.ones(len(dates))
        valid = idx < len(fdf)
        out[valid] = suffix[idx[valid]]
        return pd.Series(out, index=dates.index)
