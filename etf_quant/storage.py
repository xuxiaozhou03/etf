"""SQLite 本地存储：基于 etf_quant.model 数据模型生成表结构并读写。

表结构与模型一一对应（见 model.py），本模块只负责 SQL 生成与数据转换。
行情/区间收益等派生指标不落库，由本模块从日K线实时推导。
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from etf_quant.model import ALL_MODELS, AdjustFactor, CrawlState, DailyKline, EtfList, FloatShare

log = logging.getLogger(__name__)

_SCHEMA = "\n".join(model.create_sql() for model in ALL_MODELS)

# 区间收益回看窗口（交易日数）：周/月/季/半年/年/三年/五年
_LOOKBACK = {
    "weekly": 5, "monthly": 21, "quarterly": 63, "halfyear": 126,
    "yearly": 252, "threeYear": 756, "fiveYear": 1260,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _cumulative_factor(dates: pd.Series, factors: List[List]) -> pd.Series:
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


def _migrate_dropped_columns(conn: sqlite3.Connection, model: type) -> None:
    """删除表中存在、但模型已移除的列（Schema 演进时清理旧列）。"""
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({model.table})").fetchall()}
    dropped = sorted(existing - set(model.names()))
    for col in dropped:
        conn.execute(f"ALTER TABLE {model.table} DROP COLUMN {col}")
    if dropped:
        log.info("迁移 %s：删除旧列 %s", model.table, ", ".join(dropped))


def _upsert_sql(model: type) -> str:
    """生成 INSERT ... ON CONFLICT DO UPDATE 语句。"""
    cols = model.names()
    placeholders = ",".join(["?"] * len(cols))
    updates = ",".join(f"{c}=excluded.{c}" for c in model.non_key_names())
    return (
        f"INSERT INTO {model.table} ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT({', '.join(model.primary_keys)}) DO UPDATE SET {updates}"
    )


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(_SCHEMA)
        for model in ALL_MODELS:
            _migrate_dropped_columns(self.conn, model)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ---------- ETF 列表 ----------

    def upsert_etf_list(self, df: pd.DataFrame) -> int:
        """写入/更新 ETF 列表（df 列名与 EtfList 模型一致，缺失列自动补空）。"""
        if df.empty:
            return 0
        rows = df.copy()
        for col in EtfList.names():
            if col not in rows.columns:
                rows[col] = None
        cols = EtfList.names()
        sql = _upsert_sql(EtfList)
        values = [tuple(None if pd.isna(v) else v for v in row) for row in rows[cols].itertuples(index=False)]
        self.conn.executemany(sql, values)
        self.conn.commit()
        return len(rows)

    def load_etf_list(self) -> pd.DataFrame:
        return pd.read_sql_query(f"SELECT * FROM {EtfList.table}", self.conn)

    # ---------- 日K线 ----------

    def upsert_kline(self, code: str, df: pd.DataFrame) -> int:
        """写入/更新单只标的日K线（df 列名与 DailyKline 模型一致）。"""
        if df.empty:
            return 0
        rows = df.copy()
        rows["code"] = code
        cols = DailyKline.names()
        sql = _upsert_sql(DailyKline)
        values = [
            tuple(None if pd.isna(v) else v for v in row)
            for row in rows[cols].itertuples(index=False)
        ]
        self.conn.executemany(sql, values)
        self.conn.commit()
        return len(rows)

    def upsert_factors(self, code: str, factors: List[List]) -> int:
        """写入复权因子（factors: [[date_int, factor], ...]）。"""
        if not factors:
            return 0
        sql = _upsert_sql(AdjustFactor)
        values = [(code, str(f[0]), float(f[1])) for f in factors]
        self.conn.executemany(sql, values)
        self.conn.commit()
        return len(values)

    def upsert_float_shares(self, code: str, shares: List[List]) -> int:
        """写入流通份额（shares: [[date_int, shares], ...]）。"""
        if not shares:
            return 0
        sql = _upsert_sql(FloatShare)
        values = [(code, str(s[0]), float(s[1])) for s in shares]
        self.conn.executemany(sql, values)
        self.conn.commit()
        return len(values)

    def latest_kline_date(self, code: str) -> Optional[str]:
        row = self.conn.execute(
            f"SELECT MAX(date) FROM {DailyKline.table} WHERE code=?", (code,)
        ).fetchone()
        return row[0] if row else None

    def load_kline(self, code: str) -> pd.DataFrame:
        return pd.read_sql_query(
            f"SELECT * FROM {DailyKline.table} WHERE code=? ORDER BY date", self.conn, params=(code,)
        )

    # ---------- 实时推导（从日K线 + 复权因子计算，不落库） ----------

    def load_factors(self, code: str) -> List[List]:
        """复权因子 [[date_int, factor], ...]，按日期升序。"""
        rows = self.conn.execute(
            f"SELECT date, factor FROM {AdjustFactor.table} WHERE code=? ORDER BY date", (code,)
        ).fetchall()
        return [[r[0], r[1]] for r in rows]

    def load_float_shares(self, code: str) -> List[List]:
        """流通份额 [[date_int, shares], ...]，按日期升序。"""
        rows = self.conn.execute(
            f"SELECT date, shares FROM {FloatShare.table} WHERE code=? ORDER BY date", (code,)
        ).fetchall()
        return [[r[0], r[1]] for r in rows]

    def load_adjusted_kline(self, code: str) -> pd.DataFrame:
        """前复权日K线：在原 K 线基础上增加 adj_close 列（date 升序）。"""
        df = self.load_kline(code)
        if df.empty:
            return df
        df = df.sort_values("date").reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"])
        df["adj_close"] = df["close"] / _cumulative_factor(df["date"], self.load_factors(code))
        return df

    def latest_quote(self, code: str) -> Dict[str, Optional[float]]:
        """最新交易日行情（价格/涨跌幅%/成交额），从日K线推导。"""
        df = self.load_kline(code)
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

    def period_returns(self, code: str) -> Dict[str, Optional[float]]:
        """区间收益率（前复权），键名沿用原快照字段：weeklyPerformance 等。"""
        df = self.load_adjusted_kline(code)
        if df.empty:
            return {}
        latest = df["adj_close"].iloc[-1]
        result: Dict[str, float] = {}
        for name, lookback in _LOOKBACK.items():
            if len(df) > lookback:
                result[f"{name}Performance"] = latest / df["adj_close"].iloc[-lookback - 1] - 1
        cur_year = df["date"].iloc[-1].year
        prev_year = df[df["date"].dt.year < cur_year]
        base = prev_year["adj_close"].iloc[-1] if not prev_year.empty else df["adj_close"].iloc[0]
        result["ytdPerformance"] = latest / base - 1
        result["inceptionPerformance"] = latest / df["adj_close"].iloc[0] - 1
        return {k: round(v, 4) for k, v in result.items()}

    # ---------- 抓取状态 ----------

    def mark_success(self, code: str) -> None:
        self.conn.execute(
            f"INSERT INTO {CrawlState.table} (code, status, last_success_at, updated_at) VALUES (?, 'ok', ?, ?) "
            f"ON CONFLICT(code) DO UPDATE SET status='ok', last_success_at=excluded.last_success_at, "
            f"last_error=NULL, updated_at=excluded.updated_at",
            (code, _now(), _now()),
        )
        self.conn.commit()

    def mark_error(self, code: str, error: str) -> None:
        self.conn.execute(
            f"INSERT INTO {CrawlState.table} (code, status, last_error, updated_at) VALUES (?, 'error', ?, ?) "
            f"ON CONFLICT(code) DO UPDATE SET status='error', last_error=excluded.last_error, "
            f"updated_at=excluded.updated_at",
            (code, error[:500], _now()),
        )
        self.conn.commit()

    def load_state(self) -> Dict[str, str]:
        rows = self.conn.execute(f"SELECT code, status FROM {CrawlState.table}").fetchall()
        return {code: status for code, status in rows}

    def stats(self) -> Dict[str, int]:
        return {
            "etf_count": self.conn.execute(f"SELECT COUNT(*) FROM {EtfList.table}").fetchone()[0],
            "kline_rows": self.conn.execute(f"SELECT COUNT(*) FROM {DailyKline.table}").fetchone()[0],
            "kline_codes": self.conn.execute(f"SELECT COUNT(DISTINCT code) FROM {DailyKline.table}").fetchone()[0],
            "ok": self.conn.execute(f"SELECT COUNT(*) FROM {CrawlState.table} WHERE status='ok'").fetchone()[0],
            "error": self.conn.execute(f"SELECT COUNT(*) FROM {CrawlState.table} WHERE status='error'").fetchone()[0],
        }
