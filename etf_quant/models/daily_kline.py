"""日K线表：schema + 读写 + 前复权派生指标。"""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional

import pandas as pd

from etf_quant.models.adjust_factor import AdjustFactor
from etf_quant.models.base import ColumnDef, Model

# 区间收益回看窗口（交易日数）：周/月/季/半年/年/三年/五年
LOOKBACK = {
    "weekly": 5, "monthly": 21, "quarterly": 63, "halfyear": 126,
    "yearly": 252, "threeYear": 756, "fiveYear": 1260,
}


class DailyKline(Model):
    """日K线（芝士财富 dayKV2，字段顺序 [date, prev_close, open, high, low, close, volume, amount]）。"""

    table = "daily_kline"
    columns: List[ColumnDef] = [
        ("code", "TEXT", "NOT NULL"),
        ("date", "TEXT", "NOT NULL"),
        ("open", "REAL", ""),
        ("close", "REAL", ""),
        ("high", "REAL", ""),
        ("low", "REAL", ""),
        ("prev_close", "REAL", ""),
        ("volume", "REAL", ""),
        ("amount", "REAL", ""),
    ]
    primary_keys: List[str] = ["code", "date"]

    @classmethod
    def upsert(cls, conn: sqlite3.Connection, code: str, df: pd.DataFrame) -> int:
        """写入/更新单只标的全量日K线（df 列名与模型一致）。"""
        if df.empty:
            return 0
        rows = df.copy()
        rows["code"] = code
        cols = cls.names()
        sql = cls.upsert_sql()
        values = [
            tuple(None if pd.isna(v) else v for v in row)
            for row in rows[cols].itertuples(index=False)
        ]
        conn.executemany(sql, values)
        conn.commit()
        return len(rows)

    @classmethod
    def load(cls, conn: sqlite3.Connection, code: str) -> pd.DataFrame:
        """读取单只标的全量日K线（date 升序）。"""
        return pd.read_sql_query(
            f"SELECT * FROM {cls.table} WHERE code=? ORDER BY date", conn, params=(code,)
        )

    @classmethod
    def latest_date(cls, conn: sqlite3.Connection, code: str) -> Optional[str]:
        """最新K线日期。"""
        row = conn.execute(f"SELECT MAX(date) FROM {cls.table} WHERE code=?", (code,)).fetchone()
        return row[0] if row else None

    @classmethod
    def load_adjusted(cls, conn: sqlite3.Connection, code: str) -> pd.DataFrame:
        """前复权日K线：在原 K 线基础上增加 adj_close 列（date 升序）。"""
        return cls.load_full_adjusted(conn, code)[
            [c for c in cls.names() + ["adj_close"] if c != "code"]
        ]

    @classmethod
    def load_full_adjusted(cls, conn: sqlite3.Connection, code: str) -> pd.DataFrame:
        """前复权完整 OHLC：原 K 线 + adj_open/high/low/close（date 升序）。

        全部价格乘同一累计系数（adj_x = x / cum_factor，最新价=原始价）。
        保留原始 prev_close（涨跌停判定需用原始价），date 转 datetime。
        """
        df = cls.load(conn, code)
        if df.empty:
            return df
        df = df.sort_values("date").reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"])
        cum_factor = AdjustFactor.cumulative_factor(df["date"], AdjustFactor.load(conn, code))
        for col in ("open", "high", "low", "close"):
            df[f"adj_{col}"] = df[col] / cum_factor
        return df

    @classmethod
    def latest_quote(cls, conn: sqlite3.Connection, code: str) -> Dict[str, Optional[float]]:
        """最新交易日行情（价格/涨跌幅%/成交额），从日K线推导。"""
        df = cls.load(conn, code)
        if df.empty:
            return {}
        last = df.iloc[-1]
        change = None
        if last["prev_close"]:
            change = round((last["close"] - last["prev_close"]) / last["prev_close"] * 100, 2)
        return {
            "date": last["date"],
            "price": last["close"],
            "changePercent": change,
            "amount": last["amount"],
        }

    @classmethod
    def period_returns(cls, conn: sqlite3.Connection, code: str) -> Dict[str, Optional[float]]:
        """区间收益率（前复权），键名沿用原快照字段：weeklyPerformance 等。"""
        df = cls.load_adjusted(conn, code)
        if df.empty:
            return {}
        latest = df["adj_close"].iloc[-1]
        result: Dict[str, float] = {}
        for name, lookback in LOOKBACK.items():
            if len(df) > lookback:
                result[f"{name}Performance"] = latest / df["adj_close"].iloc[-lookback - 1] - 1
        cur_year = df["date"].iloc[-1].year
        prev_year = df[df["date"].dt.year < cur_year]
        base = prev_year["adj_close"].iloc[-1] if not prev_year.empty else df["adj_close"].iloc[0]
        result["ytdPerformance"] = latest / base - 1
        result["inceptionPerformance"] = latest / df["adj_close"].iloc[0] - 1
        return {k: round(v, 4) for k, v in result.items()}
