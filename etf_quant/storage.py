"""SQLite 本地存储：基于 etf_quant.model 数据模型生成表结构并读写。

表结构与模型一一对应（见 model.py），本模块只负责 SQL 生成与数据转换。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd

from etf_quant.model import ALL_MODELS, AdjustFactor, CrawlState, DailyKline, EtfList, Model

_SCHEMA = "\n".join(model.create_sql() for model in ALL_MODELS)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ---------- ETF 列表 ----------

    def upsert_etf_list(self, df: pd.DataFrame) -> int:
        """写入/更新 ETF 列表快照（df 列名与 EtfList 模型一致，缺失列自动补空）。"""
        if df.empty:
            return 0
        rows = df.copy()
        for col in EtfList.names():
            if col not in rows.columns:
                rows[col] = None
        rows["fetched_at"] = _now()
        if "tradeDate" in rows.columns:
            rows["tradeDate"] = rows["tradeDate"].astype(str)
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

    def latest_kline_date(self, code: str) -> Optional[str]:
        row = self.conn.execute(
            f"SELECT MAX(date) FROM {DailyKline.table} WHERE code=?", (code,)
        ).fetchone()
        return row[0] if row else None

    def load_kline(self, code: str) -> pd.DataFrame:
        return pd.read_sql_query(
            f"SELECT * FROM {DailyKline.table} WHERE code=? ORDER BY date", self.conn, params=(code,)
        )

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
