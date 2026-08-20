"""SQLite 本地存储：连接管理 + 建表 + 迁移 + 跨表统计。

各表的 schema、读写与派生查询由 etf_quant.models 包自维护；
本模块只保留数据库连接与薄门面，方法转发到对应 model 类方法。
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Dict, Optional

from etf_quant.models import ALL_MODELS, AdjustFactor, CrawlState, DailyKline, EtfList, FloatShare

log = logging.getLogger(__name__)

_SCHEMA = "\n".join(model.create_sql() for model in ALL_MODELS)


def _migrate_dropped_columns(conn: sqlite3.Connection, model: type) -> None:
    """删除表中存在、但模型已移除的列（Schema 演进时清理旧列）。"""
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({model.table})").fetchall()}
    dropped = sorted(existing - set(model.names()))
    for col in dropped:
        conn.execute(f"ALTER TABLE {model.table} DROP COLUMN {col}")
    if dropped:
        log.info("迁移 %s：删除旧列 %s", model.table, ", ".join(dropped))


class SQLiteStore:
    """数据库会话：持有连接，建表/迁移在打开时自动执行，业务方法转发到各 model。"""

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

    def upsert_etf_list(self, df) -> int:
        return EtfList.upsert(self.conn, df)

    def load_etf_list(self):
        return EtfList.load(self.conn)

    # ---------- 日K线 ----------

    def upsert_kline(self, code: str, df) -> int:
        return DailyKline.upsert(self.conn, code, df)

    def load_kline(self, code: str):
        return DailyKline.load(self.conn, code)

    def latest_kline_date(self, code: str) -> Optional[str]:
        return DailyKline.latest_date(self.conn, code)

    def load_adjusted_kline(self, code: str):
        return DailyKline.load_adjusted(self.conn, code)

    def latest_quote(self, code: str):
        return DailyKline.latest_quote(self.conn, code)

    def period_returns(self, code: str):
        return DailyKline.period_returns(self.conn, code)

    # ---------- 复权因子 / 流通份额 ----------

    def upsert_factors(self, code: str, factors) -> int:
        return AdjustFactor.upsert(self.conn, code, factors)

    def load_factors(self, code: str):
        return AdjustFactor.load(self.conn, code)

    def upsert_float_shares(self, code: str, shares) -> int:
        return FloatShare.upsert(self.conn, code, shares)

    def load_float_shares(self, code: str):
        return FloatShare.load(self.conn, code)

    # ---------- 抓取状态 ----------

    def mark_success(self, code: str) -> None:
        CrawlState.mark_success(self.conn, code)

    def mark_error(self, code: str, error: str) -> None:
        CrawlState.mark_error(self.conn, code, error)

    def load_state(self) -> Dict[str, str]:
        return CrawlState.load_status(self.conn)

    # ---------- 统计（跨表） ----------

    def stats(self) -> Dict[str, int]:
        return {
            "etf_count": self.conn.execute(f"SELECT COUNT(*) FROM {EtfList.table}").fetchone()[0],
            "kline_rows": self.conn.execute(f"SELECT COUNT(*) FROM {DailyKline.table}").fetchone()[0],
            "kline_codes": self.conn.execute(f"SELECT COUNT(DISTINCT code) FROM {DailyKline.table}").fetchone()[0],
            "ok": self.conn.execute(f"SELECT COUNT(*) FROM {CrawlState.table} WHERE status='ok'").fetchone()[0],
            "error": self.conn.execute(f"SELECT COUNT(*) FROM {CrawlState.table} WHERE status='error'").fetchone()[0],
        }
